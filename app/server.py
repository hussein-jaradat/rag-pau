"""Web product (bonus criterion): chat UI (Arabic RTL + English), login, saved
conversations, admin dashboard (analytics + knowledge gaps), document upload with
re-indexing, feedback, and a JSON API usable by a WhatsApp bot or a website widget.

    python -m app.server          ->  http://localhost:8000
"""
from __future__ import annotations

import functools
import json
import re
import sqlite3
import threading
import time
from collections import defaultdict, deque
from pathlib import Path

from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from rag.config import ROOT, settings
from rag.ingest import SUPPORTED
from rag.pipeline import RAG

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = settings.secret_key
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024          # 25 MB upload limit
_rag_lock = threading.Lock()
rag = RAG()

# ------------------------------------------------------------------ privacy: PII redaction
PII = [(re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[email]"),
       (re.compile(r"(?:\+?970|\+?972|0)5\d[\s-]?\d{3}[\s-]?\d{4}"), "[phone]"),
       (re.compile(r"\b\d{9}\b"), "[id]")]


def redact(text: str) -> str:
    for rx, rep in PII:
        text = rx.sub(rep, text)
    return text


# ------------------------------------------------------------------ simple rate limit
_hits: dict[str, deque] = defaultdict(deque)


def rate_limited(key: str, limit: int = 30, window: int = 60) -> bool:
    q, now = _hits[key], time.time()
    while q and now - q[0] > window:
        q.popleft()
    q.append(now)
    return len(q) > limit


# ------------------------------------------------------------------ database
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, pw TEXT,
    role TEXT DEFAULT 'user', created REAL);
CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, created REAL);
CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, chat_id INTEGER, role TEXT, content TEXT,
    meta TEXT, created REAL);
CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, question TEXT, refused INTEGER,
    confidence TEXT, latency REAL, cost REAL, sources TEXT, feedback INTEGER, lang TEXT, created REAL);
"""


def db() -> sqlite3.Connection:
    if "db" not in g:
        settings.db_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(settings.db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def _close(_):
    d = g.pop("db", None)
    if d:
        d.close()


def init_db():
    with app.app_context():
        d = db()
        d.executescript(SCHEMA)
        if not d.execute("SELECT 1 FROM users WHERE username=?", (settings.admin_user,)).fetchone():
            d.execute("INSERT INTO users(username,pw,role,created) VALUES (?,?,?,?)",
                      (settings.admin_user, generate_password_hash(settings.admin_password), "admin", time.time()))
        d.commit()


def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    return db().execute("SELECT id, username, role FROM users WHERE id=?", (uid,)).fetchone()


def admin_required(f):
    @functools.wraps(f)
    def wrap(*a, **kw):
        u = current_user()
        if not u or u["role"] != "admin":
            return (jsonify(error="admin only"), 403) if request.path.startswith("/api") \
                else redirect(url_for("login", next=request.path))
        return f(*a, **kw)
    return wrap


def roles_for(user) -> set[str]:
    """RBAC for retrieval: which document access levels this user may read."""
    if not user:
        return {"public"}
    return {"admin": {"public", "staff", "hr", "admin"}, "staff": {"public", "staff"},
            "hr": {"public", "staff", "hr"}}.get(user["role"], {"public"})


# ------------------------------------------------------------------ pages
@app.get("/")
def index():
    return render_template("index.html", profile=rag.profile, user=current_user(),
                           info=rag.index.info)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        name, pw = request.form.get("username", "").strip(), request.form.get("password", "")
        u = db().execute("SELECT * FROM users WHERE username=?", (name,)).fetchone()
        if request.form.get("action") == "register" and not u and len(name) >= 3 and len(pw) >= 6:
            db().execute("INSERT INTO users(username,pw,role,created) VALUES (?,?,?,?)",
                         (name, generate_password_hash(pw), "user", time.time()))
            db().commit()
            u = db().execute("SELECT * FROM users WHERE username=?", (name,)).fetchone()
        elif not u or not check_password_hash(u["pw"], pw):
            error = "اسم المستخدم أو كلمة المرور غير صحيحة"
            u = None
        if u:
            session["uid"] = u["id"]
            return redirect(request.args.get("next") or url_for("index"))
    return render_template("login.html", error=error, profile=rag.profile)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.get("/admin")
@admin_required
def admin():
    return render_template("admin.html", profile=rag.profile, user=current_user(), info=rag.index.info)


# ------------------------------------------------------------------ API
@app.post("/api/ask")
def api_ask():
    if rate_limited(request.remote_addr or "x"):
        return jsonify(error="Too many questions. Wait a minute and try again."), 429
    data = request.get_json(force=True, silent=True) or {}
    q = (data.get("question") or "").strip()[:1500]
    if not q:
        return jsonify(error="Type a question first."), 400
    user = current_user()
    chat_id = data.get("chat_id")
    history = data.get("history") or []
    if user and chat_id:
        rows = db().execute("SELECT role, content FROM messages WHERE chat_id=? ORDER BY id DESC LIMIT 6",
                            (chat_id,)).fetchall()
        history = [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
    with _rag_lock:
        a = rag.ask(q, history=history[-6:], roles=roles_for(user))
    out = a.to_dict()
    # persist
    d = db()
    if user:
        if not chat_id:
            cur = d.execute("INSERT INTO chats(user_id,title,created) VALUES (?,?,?)",
                            (user["id"], q[:60], time.time()))
            chat_id = cur.lastrowid
        d.execute("INSERT INTO messages(chat_id,role,content,meta,created) VALUES (?,?,?,?,?)",
                  (chat_id, "user", q, "{}", time.time()))
        d.execute("INSERT INTO messages(chat_id,role,content,meta,created) VALUES (?,?,?,?,?)",
                  (chat_id, "assistant", a.answer,
                   json.dumps({"citations": a.citations, "confidence": a.confidence,
                               "refused": a.refused}, ensure_ascii=False), time.time()))
    cur = d.execute("INSERT INTO logs(question,refused,confidence,latency,cost,sources,feedback,lang,created)"
                    " VALUES (?,?,?,?,?,?,?,?,?)",
                    (redact(q), int(a.refused), a.confidence, a.timings.get("total", 0), a.cost_usd,
                     json.dumps(sorted({c["source"] for c in a.citations}), ensure_ascii=False),
                     None, a.lang, time.time()))
    d.commit()
    out["chat_id"] = chat_id
    out["log_id"] = cur.lastrowid
    return jsonify(out)


@app.post("/api/feedback")
def api_feedback():
    data = request.get_json(force=True, silent=True) or {}
    db().execute("UPDATE logs SET feedback=? WHERE id=?", (1 if data.get("up") else -1, data.get("log_id")))
    db().commit()
    return jsonify(ok=True)


@app.get("/api/chats")
def api_chats():
    u = current_user()
    if not u:
        return jsonify([])
    rows = db().execute("SELECT id, title, created FROM chats WHERE user_id=? ORDER BY id DESC LIMIT 50",
                        (u["id"],)).fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/api/chats/<int:cid>")
def api_chat(cid):
    u = current_user()
    owner = db().execute("SELECT user_id FROM chats WHERE id=?", (cid,)).fetchone()
    if not u or not owner or owner["user_id"] != u["id"]:
        return jsonify(error="not found"), 404
    rows = db().execute("SELECT role, content, meta FROM messages WHERE chat_id=? ORDER BY id", (cid,)).fetchall()
    return jsonify([{"role": r["role"], "content": r["content"], "meta": json.loads(r["meta"] or "{}")}
                    for r in rows])


@app.get("/api/health")
def api_health():
    return jsonify(ok=True, domain=settings.domain, index=rag.index.info,
                   llm=f"{settings.llm_provider}:{settings.default_model()}", llm_ready=rag.llm.available)


@app.get("/api/analytics")
@admin_required
def api_analytics():
    d = db()
    tot = d.execute("SELECT COUNT(*) n, AVG(latency) lat, SUM(cost) cost, AVG(refused) ref,"
                    " SUM(feedback=1) up, SUM(feedback=-1) down FROM logs").fetchone()
    top = d.execute("SELECT question, COUNT(*) n FROM logs GROUP BY lower(question) ORDER BY n DESC LIMIT 10").fetchall()
    gaps = d.execute("SELECT question, COUNT(*) n FROM logs WHERE refused=1 OR feedback=-1 "
                     "GROUP BY lower(question) ORDER BY n DESC LIMIT 10").fetchall()
    per_day = d.execute("SELECT date(created,'unixepoch') day, COUNT(*) n FROM logs GROUP BY day ORDER BY day").fetchall()
    src = defaultdict(int)
    for r in d.execute("SELECT sources FROM logs"):
        for s in json.loads(r["sources"] or "[]"):
            src[s] += 1
    ev = ROOT / "eval" / "results.json"
    return jsonify(
        totals={"questions": tot["n"] or 0, "avg_latency": round(tot["lat"] or 0, 2),
                "cost": round(tot["cost"] or 0, 4), "refusal_rate": round(tot["ref"] or 0, 3),
                "up": tot["up"] or 0, "down": tot["down"] or 0,
                "users": d.execute("SELECT COUNT(*) FROM users").fetchone()[0]},
        top=[dict(r) for r in top], gaps=[dict(r) for r in gaps], per_day=[dict(r) for r in per_day],
        sources=sorted(src.items(), key=lambda x: -x[1])[:10],
        eval=json.loads(ev.read_text(encoding="utf-8")) if ev.exists() else None)


@app.get("/api/docs")
@admin_required
def api_docs():
    out = []
    for p in sorted(settings.docs_dir.rglob("*")):
        if p.is_file() and not p.name.startswith(("_", ".")):
            n = sum(1 for c in rag.index.chunks if c.source == str(p.relative_to(settings.docs_dir)))
            out.append({"name": str(p.relative_to(settings.docs_dir)), "kb": round(p.stat().st_size / 1024, 1),
                        "chunks": n})
    return jsonify(out)


@app.post("/api/upload")
@admin_required
def api_upload():
    saved = []
    for f in request.files.getlist("files"):
        name = secure_filename(f.filename or "")
        if not name:                                   # secure_filename drops Arabic names
            ext = Path(f.filename or "").suffix.lower()
            name = f"doc_{int(time.time() * 1000)}{ext}"
        if Path(name).suffix.lower() not in SUPPORTED:
            continue
        f.save(settings.docs_dir / name)
        saved.append(name)
    report = None
    if saved:
        with _rag_lock:
            report = rag.rebuild()
    return jsonify(saved=saved, report=report)


@app.delete("/api/docs/<path:name>")
@admin_required
def api_delete_doc(name):
    p = (settings.docs_dir / name).resolve()
    if settings.docs_dir.resolve() not in p.parents or not p.exists():
        return jsonify(error="not found"), 404
    p.unlink()
    with _rag_lock:
        report = rag.rebuild()
    return jsonify(report=report)


@app.post("/api/reindex")
@admin_required
def api_reindex():
    with _rag_lock:
        return jsonify(report=rag.rebuild())


init_db()

if __name__ == "__main__":
    print(f"\n  {rag.profile['title_ar']}  ->  http://localhost:{settings.port}\n"
          f"  index: {rag.index.info.get('chunks')} chunks · {rag.index.info.get('embedder')}\n"
          f"  llm:   {settings.llm_provider} ({'ready' if rag.llm.available else 'offline/extractive'})\n")
    app.run(host="0.0.0.0", port=settings.port, debug=False, threaded=True)
