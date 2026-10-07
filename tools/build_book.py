#!/usr/bin/env python3
"""Build the reader and Markdown chapters from the skill's canonical catalogs."""
import argparse
from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "china-development"
sys.path.insert(0, str(SKILL / "scripts"))
import cards as card_tools

CHAPTERS = [
    ("national", "national.md", "国家发展", "从理论、历史和规划进入发展目标、政策效果与未来情景。"),
    ("local_industry", "industry.md", "地方与产业", "把国家方向落实为需求、资源、执行主体与可检验的项目选择。"),
    ("household_personal", "personal.md", "家庭与个人", "结合所在地规则和自身约束，处理就业、住房、养老、培训与创业。"),
]
FIELDS = [("required_context", "先补哪些条件"), ("actions", "行动步骤"),
          ("costs", "成本"), ("expected_benefits", "预期作用"), ("tradeoffs", "取舍"),
          ("stop_conditions", "暂停或改判条件"), ("local_verification", "本地核验")]


def make_reader(entries, sources, compiled_on):
    articles = []
    for card in entries:
        searchable = escape(json.dumps(card, ensure_ascii=False).casefold(), quote=True)
        bits = [f'<article data-level="{card["level"]}" data-search="{searchable}">',
                f'<details id="{card["id"]}"><summary><span class="tag">{card_tools.LABELS[card["level"]]}</span>',
                f'<strong>{escape(card["title"])}</strong><small>{escape(card["applies_to"])}</small></summary>',
                f'<div class="body"><p class="meta">条目 {card["id"]} · 核验 {card["checked_date"]}</p>']
        for field, label in FIELDS:
            bits.append(f'<h3>{label}</h3><ul>')
            bits.extend(f'<li>{escape(value)}</li>' for value in card[field])
            bits.append('</ul>')
        bits.append('<h3>证据及其支持范围</h3><ul>')
        for ev in card["evidence"]:
            source = sources[ev["source_id"]]
            bits.append(f'<li><a href="{escape(source["url"], quote=True)}">{escape(source["title"])}</a>'
                        f'（{card_tools.KIND_LABELS[ev["type"]]}；{escape(ev["locator"])}）：{escape(ev["supports"])}</li>')
        bits.extend(['</ul>', f'<p><b>复查信号：</b>{escape(card["review_trigger"])}</p>',
                     f'<p><b>边界：</b>{escape(card["limits"])}</p>', '</div></details></article>'])
        articles.append('\n'.join(bits))
    return '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>How to Live Better with the Party · 在党的光辉下，如何过得更好</title>
<meta name="description" content="以历届领导人论述、党政公开文献和统计证据，贯通国家、产业与个人决策。">
<style>
:root{color-scheme:light;--ink:#16352c;--muted:#52675d;--line:#d6dfd4;--paper:#f5f5ed;--accent:#215b46}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}
header,main,footer{max-width:1100px;margin:auto;padding:36px 28px}header{padding-top:60px;border-bottom:1px solid var(--line)}
.eyebrow{font-size:12px;letter-spacing:.15em;color:var(--accent);font-weight:700}h1{font-size:clamp(28px,4vw,46px);line-height:1.3;max-width:940px;margin:18px 0}
.lead{font-size:19px;max-width:900px}a{color:var(--accent);text-underline-offset:3px}nav{display:flex;flex-wrap:wrap;gap:10px 24px;margin-top:24px}
.focus{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:28px 0}.focus div{padding:20px;background:#e8edde;border-radius:12px}.focus b{display:block}.focus p{margin:8px 0 0;color:var(--muted)}
.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:end;margin:26px 0 12px}label{display:grid;gap:6px;font-size:14px}label:first-child{flex:1;min-width:220px}
input,select{font:inherit;color:var(--ink);padding:12px;background:white;border:1px solid #93aa9b;border-radius:8px}input:focus,select:focus{outline:3px solid #b5d2b5}
.meta{font-size:13px;color:var(--muted)}article{background:white;border:1px solid var(--line);border-radius:12px;margin:14px 0;overflow:hidden}summary{padding:23px;cursor:pointer}summary strong{font-size:19px;margin-left:12px}summary small{display:block;font-size:15px;color:var(--muted);margin-top:9px}.tag{font-size:12px;background:#eaf1e8;border-radius:4px;padding:4px 7px;white-space:nowrap}
.body{padding:0 26px 22px;border-top:1px solid var(--line)}h3{font-size:16px;margin:24px 0 8px}.body ul{padding-left:22px}footer{font-size:13px;border-top:1px solid var(--line);color:var(--muted)}[hidden]{display:none!important}
@media(max-width:650px){header,main,footer{padding:24px 18px}.focus{grid-template-columns:1fr;gap:10px}.focus div{padding:16px}summary strong{display:block;margin:9px 0}summary{padding:18px}}
</style></head><body>
<header><div class="eyebrow">HOW TO LIVE BETTER WITH THE PARTY</div>
<h1>在党的光辉下<br>如何过得更好</h1>
<p>中国特色社会主义与中国发展实用指南。“党”指中国共产党（the Communist Party of China）。</p>
<p class="lead">以中国特色社会主义理论为主线，以历届领导人论述、党和政府公开文献及统计证据为基础，理解中国发展的过去、现在与未来，支持国家、产业和个人的具体选择。</p>
<nav><a href="README.md">项目说明</a><a href="book/README.md">完整目录</a><a href="skills/china-development/references/theory-history.md">理论与历史</a><a href="skills/china-development/SKILL.md">使用 AI Skill</a><a href="https://github.com/HermitSong/howtolivebetterwiththeparty">GitHub</a></nav>
</header><main>
<div class="focus"><div><b>理论与文献</b><p>毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，以及其他领导人的相关公开文献。</p></div>
<div><b>历史、现实与未来</b><p>回到历史语境，核验现行政策与发展结果，依据假设和指标构建未来情景。</p></div>
<div><b>从国家到个人</b><p>国家方向 → 政策工具 → 执行主体 → 地方规则 → 自身条件 → 可验证结果。</p></div></div>
<h2>按问题查行动条目</h2><p>先看适用条件，再比较行动、成本、取舍和暂停条件。理论论述、规则文本与政策实际效果分别判断。</p>
<p class="meta">资料快照：''' + compiled_on + f''' · {len(entries)} 个行动条目 · {len(sources)} 条来源记录。来源目录并非全文数据库，门户不等于已读正文；现行资格、金额和时限需要当次核验。</p>
<div class="controls"><label for="query">关键词<input id="query" type="search" placeholder="例如：产业园、社保、培训、共同富裕"></label>
<label for="level">决策层级<select id="level"><option value="">全部层级</option><option value="national">国家发展</option><option value="local_industry">地方与产业</option><option value="household_personal">家庭与个人</option></select></label></div>
<p id="count" class="meta" aria-live="polite">全部 {len(entries)} 条</p><p id="empty" hidden>没有匹配条目。可换关键词，或按照理论与来源导航继续研究；没有收录不代表没有相关政策。</p>
''' + '\n'.join(articles) + '''
</main><footer>原创研究与行动指南；结构借鉴 <a href="https://github.com/eternity4719/HowToLiveBetter">HowToLiveBetter</a>。不隶属党政机关。当前是有限种子库；未来规划目标不等于预测结果。许可范围见仓库说明。</footer>
<script>
const query=document.querySelector('#query'),level=document.querySelector('#level'),items=[...document.querySelectorAll('article')];
function filter(){const terms=query.value.toLocaleLowerCase().trim().split(/\\s+/).filter(Boolean);let count=0;for(const item of items){const show=(!level.value||item.dataset.level===level.value)&&terms.every(t=>item.dataset.search.includes(t));item.hidden=!show;if(show)count++;}document.querySelector('#count').textContent=`显示 ${count} / ${items.length} 条 · 原始目录顺序不代表推荐排名`;document.querySelector('#empty').hidden=count!==0;}
query.addEventListener('input',filter);level.addEventListener('change',filter);
if(location.hash){const target=document.getElementById(location.hash.slice(1));if(target&&target.tagName==='DETAILS')target.open=true;}
</script></body></html>
'''


def outputs():
    catalog = json.loads((SKILL / "references/source-catalog.json").read_text(encoding="utf-8-sig"))
    collection = json.loads((SKILL / "references/decision-cards.json").read_text(encoding="utf-8-sig"))
    errors = card_tools.validate(collection, catalog)
    if errors:
        raise ValueError("; ".join(errors))
    entries = collection["cards"]
    sources = {s["id"]: s for s in catalog["sources"]}
    result = {}
    toc = ["# How to Live Better with the Party · 阅读目录", "",
           "**在党的光辉下，如何过得更好** · 中国特色社会主义与中国发展实用指南", "",
           "以中国特色社会主义理论和公开文献为基础，贯通历史、现实与未来，连接国家、地方产业、家庭个人决策。", "",
           "[项目首页](../README.md) · [项目重点](../docs/project-focus.md) · [理论与历史](../skills/china-development/references/theory-history.md) · [证据方法](../skills/china-development/references/research-method.md)", "",
           f"资料快照：{catalog['compiled_on']}。行动条目是研究和决策起点；预期作用不等于已证实效果。具体政策须按时间、地区和资格重新核验。", ""]
    for level, filename, title, description in CHAPTERS:
        subset = [card for card in entries if card["level"] == level]
        toc += [f"## {title}", "", description, ""]
        for card in subset:
            toc.append(f"- [{card['title']}]({filename}#{card['id']})")
        toc.append("")
        body = card_tools.render(subset, sources)
        body = body.replace("# 中国发展与民生行动条目", f"# {title}", 1)
        body = body.replace("由 decision-cards.json 自动生成。", "[返回目录](README.md) · 由技能内的 decision-cards.json 自动生成。", 1)
        for card in subset:
            body = body.replace(f"## {card['id']} · {card['title']}",
                                f'<a id="{card["id"]}"></a>\n\n## {card["title"]}')
        result[ROOT / "book" / filename] = body.rstrip() + "\n"
    result[ROOT / "book/README.md"] = '\n'.join(toc).rstrip() + "\n"
    result[SKILL / "references/decision-cards.md"] = card_tools.render(entries, sources).rstrip() + "\n"
    result[ROOT / "index.html"] = make_reader(entries, sources, catalog["compiled_on"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mismatches = []
    for path, content in outputs().items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                mismatches.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if mismatches:
        print("Generated files need rebuilding: " + ", ".join(mismatches))
        return 1
    print("Generated reader, 3 chapters, contents and skill reference: " + ("consistent" if args.check else "written"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
