#!/usr/bin/env python3
"""Build the UNIFIED static Academy page: every lesson = video + full theory + quiz.
Source of truth = боевой course_content.json (theory + quizzes). Videos = local
videos/urokNN_<id>.mp4 (already in this repo). No login, progress in localStorage.
Output: academy.html
"""
import json, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CC = json.loads((Path.home() / "Documents/AI/atamura-academy/app/data/course_content.json").read_text(encoding="utf-8"))
VID = ROOT / "videos"
e = lambda s: html.escape(str(s), quote=True)

PHASES = {"core": "База продаж · ядро", "prof": "Профессия телемаркетолога",
          "call": "Этапы входящего звонка", "assemble": "Сборка звонка"}
mods = CC["modules"]
NUM = {m["id"]: f"{i+1:02d}" for i, m in enumerate(mods)}


def video_file(mid):
    n = NUM[mid]
    for f in VID.glob(f"urok{n}_*.mp4"):
        return f.name
    return None


def render_step(s):
    t = s["t"]
    if t == "media":
        return ""  # video rendered separately at top of lesson
    if t == "point":
        return f'<div class="pt"><h4>{e(s.get("h",""))}</h4><div class="bd">{s.get("b","")}</div></div>'
    if t == "script":
        return f'<div class="scr"><h4>📞 {e(s.get("h",""))}</h4><div class="bd">{s.get("s","")}</div></div>'
    if t == "dialogue":
        var = s.get("variant", "")
        cls = "dlg-bad" if var == "bad" else "dlg-good"
        mark = "❌" if var == "bad" else "✅"
        rows = "".join(
            f'<div class="ln"><span class="who">{e(l.get("who",""))}:</span> {e(l.get("text",""))}</div>'
            for l in s.get("lines", []))
        why = f'<div class="why">{e(s.get("why",""))}</div>' if s.get("why") else ""
        return f'<div class="dlg {cls}"><h4>{mark} {e(s.get("h",""))}</h4>{rows}{why}</div>'
    return ""


def render_quiz(mid, quiz):
    if not quiz:
        return ""
    items = []
    for qi, q in enumerate(quiz):
        opts = "".join(
            f'<label class="opt"><input type="radio" name="{mid}_{qi}" value="{oi}">'
            f'<span>{e(o)}</span></label>'
            for oi, o in enumerate(q.get("o", [])))
        items.append(
            f'<div class="q" data-a="{q.get("a",0)}" data-e="{e(q.get("e",""))}">'
            f'<div class="qt">{qi+1}. {e(q.get("q",""))}</div>{opts}'
            f'<div class="exp"></div></div>')
    return (f'<div class="quiz" data-lesson="{mid}"><h4>🎯 Проверь себя ({len(quiz)} вопр.)</h4>'
            + "".join(items)
            + f'<button class="check" onclick="checkQuiz(this,\'{mid}\')">Проверить</button>'
            + '<div class="qres"></div></div>')


def render_lesson(i, m):
    mid = m["id"]; n = NUM[mid]
    vf = video_file(mid)
    if vf:
        poster = f"videos/posters/{vf[:-4]}.jpg"
        video = (f'<video controls preload="none" playsinline poster="{poster}" '
                 f'src="videos/{vf}"></video>')
    else:
        video = '<div class="soon">⏳ Видео скоро — догенерируется после пополнения квоты движка.</div>'
    media = next((s for s in m["lesson"] if s["t"] == "media"), None)
    cap = f'<div class="vcap">{e(media.get("cap",""))}</div>' if media and media.get("cap") else ""
    theory = "".join(render_step(s) for s in m["lesson"])
    quiz = render_quiz(mid, m.get("quiz", []))
    return (f'<section class="lesson" id="L{n}" data-id="{mid}">'
            f'<div class="lh"><span class="lnum">{n}</span>'
            f'<h3>{e(m["title"])}</h3><span class="done" id="done_{mid}"></span></div>'
            f'{video}{cap}<div class="theory">{theory}</div>{quiz}'
            f'<a class="top" href="#top">↑ к списку уроков</a></section>')


# ---- table of contents (by phase) ----
toc = []
lastph = None
for i, m in enumerate(mods):
    ph = m["phase"]
    if ph != lastph:
        toc.append(f'<div class="toc-ph">{e(PHASES.get(ph,ph))}</div>'); lastph = ph
    vf = video_file(m["id"])
    tag = "" if vf else ' <span class="toc-soon">скоро</span>'
    toc.append(f'<a class="toc-i" href="#L{NUM[m["id"]]}"><span class="ci" id="ci_{m["id"]}"></span>'
               f'<b>{NUM[m["id"]]}</b> {e(m["title"])}{tag}</a>')

lessons = "".join(render_lesson(i, m) for i, m in enumerate(mods))
n_video = sum(1 for m in mods if video_file(m["id"]))

CSS = """
:root{--navy:#284157;--navy9:#15242f;--teal:#007484;--gold:#CFB372;--cream:#F7F5EE;--paper:#fffefb;--ink:#23303a;--muted:#5f6b75;--line:#e6e2d6;--good:#1f7a4d;--good-t:#e7f2ec;--bad:#b4232a;--bad-t:#f6e7e2}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Jost',system-ui,sans-serif;background:var(--cream);color:var(--ink);line-height:1.55;padding:0 0 70px}
header{background:linear-gradient(120deg,var(--navy),var(--navy9));color:#eef4f6;padding:22px 18px;text-align:center}
header h1{font-family:'Cormorant Garamond',Georgia,serif;font-size:27px;font-weight:700}
header .sub{color:var(--gold);font-size:13px;margin-top:4px}
.wrap{max-width:780px;margin:0 auto;padding:16px 14px}
.note{background:var(--paper);border:1px solid var(--line);border-left:3px solid var(--teal);border-radius:10px;padding:12px 14px;font-size:13.5px;color:var(--muted);margin-bottom:16px}
.toc{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:10px 8px;margin-bottom:22px}
.toc-ph{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);font-weight:700;padding:10px 10px 4px}
.toc-i{display:flex;align-items:center;gap:7px;text-decoration:none;color:var(--ink);font-size:13.5px;padding:6px 10px;border-radius:8px}
.toc-i:hover{background:var(--cream)}
.toc-i b{color:var(--teal)}
.toc-soon{font-size:10px;background:var(--gold);color:var(--navy9);border-radius:10px;padding:1px 6px;font-weight:700}
.ci{width:15px;height:15px;border-radius:50%;border:2px solid var(--line);flex-shrink:0}
.ci.ok{background:var(--good);border-color:var(--good)}
.lesson{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:0 0 14px;margin-bottom:22px;overflow:hidden;scroll-margin-top:10px}
.lh{display:flex;align-items:center;gap:12px;background:linear-gradient(120deg,var(--navy),var(--navy9));color:#eef4f6;padding:12px 16px}
.lh .lnum{width:34px;height:34px;border-radius:9px;background:var(--gold);color:var(--navy9);display:grid;place-items:center;font-family:'Cormorant Garamond',serif;font-weight:700;flex-shrink:0}
.lh h3{font-family:'Cormorant Garamond',serif;font-size:20px;font-weight:600;flex:1}
.lh .done{font-size:18px}
video{width:100%;display:block;background:#000;aspect-ratio:16/9}
.soon{margin:0;padding:26px 16px;text-align:center;color:var(--muted);font-size:13px;background:repeating-linear-gradient(45deg,#fbf9f2,#fbf9f2 10px,#f5f1e6 10px,#f5f1e6 20px)}
.vcap{font-size:12.5px;color:var(--muted);padding:9px 16px;border-bottom:1px solid var(--line);font-style:italic}
.theory{padding:6px 16px}
.pt{margin:14px 0}
.pt h4,.scr h4,.dlg h4,.quiz h4{font-size:15px;color:var(--navy);margin-bottom:5px;font-family:'Jost',sans-serif;font-weight:600}
.bd{font-size:14.5px}.bd p{margin:6px 0}.bd b{color:var(--navy)}.bd ul{margin:6px 0 6px 18px}
.scr{margin:14px 0;background:#eef4f6;border:1px solid #cfe0e6;border-radius:10px;padding:11px 14px}
.dlg{margin:14px 0;border-radius:10px;padding:11px 14px}
.dlg-good{background:var(--good-t);border:1px solid #cfe6da}.dlg-bad{background:var(--bad-t);border:1px solid #ecd3ca}
.dlg .ln{font-size:13.7px;margin:4px 0}.dlg .who{font-weight:700;color:var(--navy)}
.dlg .why{font-size:12.7px;color:var(--muted);margin-top:7px;font-style:italic}
.quiz{margin:18px 16px 4px;background:#fbfaf4;border:1px solid var(--line);border-radius:12px;padding:14px}
.q{margin:12px 0;padding-bottom:10px;border-bottom:1px dashed var(--line)}
.qt{font-weight:600;font-size:14px;margin-bottom:7px}
.opt{display:flex;gap:8px;align-items:flex-start;padding:7px 9px;border:1px solid var(--line);border-radius:8px;margin:5px 0;font-size:13.5px;cursor:pointer;background:var(--paper)}
.opt.ok{background:var(--good-t);border-color:var(--good)}
.opt.no{background:var(--bad-t);border-color:var(--bad)}
.opt input{margin-top:3px}
.exp{font-size:12.8px;color:var(--muted);margin-top:6px;display:none}
.exp.show{display:block}
.check{margin-top:8px;background:var(--teal);color:#fff;border:none;border-radius:9px;padding:10px 18px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit}
.qres{margin-top:10px;font-weight:600;font-size:14px}
.top{display:inline-block;font-size:11px;color:var(--muted);text-decoration:none;margin:10px 16px 0}
footer{text-align:center;color:var(--muted);font-size:12px;margin-top:24px}
"""

JS = """
function checkQuiz(btn,mid){
  var box=btn.closest('.quiz'),qs=box.querySelectorAll('.q'),ok=0;
  qs.forEach(function(q){
    var a=+q.dataset.a,sel=q.querySelector('input:checked');
    q.querySelectorAll('.opt').forEach(function(o){o.classList.remove('ok','no')});
    var opts=q.querySelectorAll('.opt');
    if(opts[a])opts[a].classList.add('ok');
    if(sel){var v=+sel.value;if(v===a)ok++;else if(opts[v])opts[v].classList.add('no');}
    var ex=q.querySelector('.exp');ex.textContent='💡 '+q.dataset.e;ex.classList.add('show');
  });
  var res=box.querySelector('.qres'),pass=ok===qs.length;
  res.textContent=(pass?'✅ ':'')+'Верно '+ok+' из '+qs.length+(pass?' — урок пройден!':' — повтори и попробуй снова');
  res.style.color=pass?'#1f7a4d':'#b4232a';
  if(pass){localStorage.setItem('done_'+mid,'1');mark(mid);}
}
function mark(mid){
  var d=document.getElementById('done_'+mid),c=document.getElementById('ci_'+mid);
  if(localStorage.getItem('done_'+mid)){if(d)d.textContent='✓';if(c)c.classList.add('ok');}
}
document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.lesson').forEach(function(s){mark(s.dataset.id)});
});
"""

HTML = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="robots" content="noindex, nofollow">'
        f'<title>Академия ATAMŪRA — уроки, теория и видео</title>'
        f'<link rel="preconnect" href="https://fonts.googleapis.com">'
        f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">'
        f'<style>{CSS}</style></head><body><a id="top"></a>'
        f'<header><h1>Академия ATAMŪRA</h1><div class="sub">Путь телемаркетолога · уроки · теория · видео · тесты</div></header>'
        f'<div class="wrap">'
        f'<div class="note">Полная Академия для прохождения: у каждого урока — <b>видео</b>, <b>теория</b> и <b>тест</b>. '
        f'Вход не нужен, прогресс сохраняется в этом браузере. Видео готовы для <b>{n_video} из 20</b> уроков; '
        f'остальные подтянутся после пополнения квоты движка.</div>'
        f'<div class="toc">{"".join(toc)}</div>'
        f'{lessons}'
        f'<footer>ATAMŪRA GROUP · учебный стенд, не для распространения</footer>'
        f'</div><script>{JS}</script></body></html>')

out = ROOT / "academy.html"
out.write_text(HTML, encoding="utf-8")
print(f"WROTE {out}  ({len(HTML)//1024} KB, {len(mods)} lessons, {n_video} with video)")
