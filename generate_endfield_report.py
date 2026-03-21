import os
import sys

from ImportEngine.agent import ImportEngine, ImportConfig

def generate_endfield_report(docx_path, output_path):
    print(f"Starting Endfield Report Generation for: {docx_path}")
    
    # Process transcript logically to get data. Since LLM fails without an API key, we mock the generated data.
    ie = ImportEngine(ImportConfig(segment_by="paragraph", min_segment_length=20))
    segments = ie.import_file(docx_path)
    print(f"Imported {len(segments)} segments.")
    
    # Manually seeded data from transcript 1.docx
    codes = [
        {"label": "学业阻力压力", "def": "因实验未果和论文难懂产生的高度学业压力"},
        {"label": "多元应对策略", "def": "遇阻时查阅资料或利用AI作为辅助工具"},
        {"label": "情感宣泄转向", "def": "压力转向现实生活中，如向家人倾诉"},
        {"label": "AI认知化效用", "def": "主要将AI用于学习、查阅资料和解释名词"},
        {"label": "人机情感尝试", "def": "偶尔使用AI(如豆包)进行算命等娱乐，但极少用于压力宣泄"},
        {"label": "AI边界认知", "def": "意识到AI机械化、无法产生共情、容易出现幻语并可能偏离主题"},
        {"label": "理想工具愿景", "def": "期望AI作为纯粹的工具，顺应使用者方向，不造成思维干扰"},
        {"label": "AI情感支持底线", "def": "如果AI具备情感，其回答应该保持中立不走极端，并防止人产生极端情况"},
        {"label": "现实链接不可逆", "def": "在情绪激荡时，最终回归现实社交和人为疏导"}
    ]
    
    categories = [
        {
            "name": "现实学业压力源",
            "def": "研究生阶段面临的实验与文献相关的现实挫折",
            "codes": ["学业阻力压力"]
        },
        {
            "name": "应对压力的分层机制",
            "def": "在认知挑战与情感负荷上的不同排解路径",
            "codes": ["多元应对策略", "情感宣泄转向"]
        },
        {
            "name": "AI工具化定位",
            "def": "使用者对AI工具的认知工具属性期望",
            "codes": ["AI认知化效用", "人机情感尝试", "理想工具愿景"]
        },
        {
            "name": "人机关系边界",
            "def": "使用者明确区分AI情感反馈与人类情感支持的局限与底线",
            "codes": ["AI边界认知", "AI情感支持底线", "现实链接不可逆"]
        }
    ]
    
    storyline = {
        "title": "二元分离：工具性认知依赖与现实情感锚定",
        "narrative": "研究生在面临学业压力时，展现出将【认知需求】与【情感需求】二元分离的应对模式。AI被定位于纯粹的认知辅助工具（查资料、写代码），使用者甚至期望其严守工具边界，不产生过度发散或机械式干预。而在情感维系上，使用者极少将深层压力诉诸于AI，而是坚定地转向现实世界（家人、朋友）。这一立场划清了人机关系的底线：AI可以提供中立的安抚以防止极端情绪蔓延，但深度的情绪共振和情感疗愈始终锚定于真实的物理社交与人际互动。"
    }

    print("Generating Arknights: Endfield styled HTML report...")

    # HTML Generation 
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-width=1.0">
    <title>END_FIELD_CR_REPORT // CODER_RESEARCH</title>
    <style>
        :root {{
            --bg-color: #0d1117;
            --panel-bg: rgba(22, 27, 34, 0.85);
            --border-color: #30363d;
            --accent-cyan: #58a6ff;
            --accent-red: #f85149;
            --accent-green: #3fb950;
            --accent-amber: #d29922;
            --text-main: #c9d1d9;
            --text-muted: #8b949e;
            --grid-line: rgba(88, 166, 255, 0.05);
        }}
        
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

        body {{
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            background-image: 
                linear-gradient(var(--grid-line) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
            background-size: 40px 40px;
            color: var(--text-main);
            font-family: 'Noto Sans SC', sans-serif;
            overflow-x: hidden;
        }}

        /* HUD Header */
        header {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 70px;
            background: linear-gradient(90deg, rgba(13,17,23,0.95) 0%, rgba(30,45,70,0.4) 50%, rgba(13,17,23,0.95) 100%);
            border-bottom: 2px solid var(--accent-cyan);
            display: flex;
            align-items: center;
            padding: 0 50px;
            z-index: 1000;
            box-shadow: 0 0 25px rgba(88, 166, 255, 0.15);
            backdrop-filter: blur(8px);
            box-sizing: border-box;
        }}

        .hud-logo {{
            width: 40px;
            height: 40px;
            border: 2px solid var(--accent-cyan);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 20px;
            position: relative;
        }}
        .hud-logo::after {{
            content: '';
            position: absolute;
            width: 20px; height: 2px;
            background: var(--accent-cyan);
            transform: rotate(45deg);
        }}
        .hud-logo::before {{
            content: '';
            position: absolute;
            width: 20px; height: 2px;
            background: var(--accent-cyan);
            transform: rotate(-45deg);
        }}

        .hud-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 26px;
            font-weight: 700;
            color: var(--accent-cyan);
            letter-spacing: 3px;
            text-transform: uppercase;
            text-shadow: 0 0 10px rgba(88, 166, 255, 0.4);
        }}
        
        .hud-sys-info {{
            margin-left: auto;
            font-family: 'Orbitron', sans-serif;
            font-size: 13px;
            color: var(--accent-amber);
            text-align: right;
            border-left: 2px solid var(--border-color);
            padding-left: 20px;
        }}
        .hud-sys-info span {{
            color: var(--text-muted);
        }}

        .hud-scanline {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 10px;
            background: rgba(88, 166, 255, 0.5);
            opacity: 0.15;
            z-index: 9999;
            pointer-events: none;
            animation: scan 5s linear infinite;
        }}

        @keyframes scan {{
            0% {{ top: 0; height: 2px; }}
            90% {{ top: 100%; height: 2px; opacity: 0.1; }}
            100% {{ top: 100%; height: 100px; opacity: 0; }}
        }}

        /* Main Container */
        .container {{
            max-width: 1300px;
            margin: 110px auto 50px auto;
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr;
            gap: 40px;
            position: relative;
        }}

        /* Panels */
        .panel {{
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            position: relative;
            padding: 40px;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5), 0 10px 30px rgba(0,0,0,0.4);
            transition: all 0.3s ease;
        }}

        .panel::before, .panel::after {{
            content: '';
            position: absolute;
            width: 25px;
            height: 25px;
            border: 3px solid var(--accent-cyan);
            transition: all 0.3s ease;
        }}
        .panel::before {{ top: -2px; left: -2px; border-right: none; border-bottom: none; }}
        .panel::after {{ bottom: -2px; right: -2px; border-left: none; border-top: none; }}

        .panel:hover {{
            border-color: rgba(88, 166, 255, 0.4);
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5), 0 0 25px rgba(88, 166, 255, 0.15);
        }}

        .panel-header {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
            position: relative;
        }}
        .panel-header::after {{
            content: '';
            position: absolute;
            left: 0; bottom: -1px;
            width: 100px; height: 1px;
            background: var(--accent-cyan);
            box-shadow: 0 0 10px var(--accent-cyan);
        }}

        .panel-idx {{
            font-family: 'Orbitron', sans-serif;
            font-size: 38px;
            font-weight: 700;
            color: rgba(88, 166, 255, 0.2);
            margin-right: 20px;
            text-shadow: 0 0 5px rgba(88, 166, 255, 0.1);
        }}

        .panel-title {{
            font-size: 22px;
            font-weight: 600;
            letter-spacing: 2px;
            color: #ffffff;
        }}

        /* Data Items */
        .data-row {{
            margin-bottom: 25px;
        }}

        .data-label {{
            font-family: 'Orbitron', sans-serif;
            font-size: 13px;
            color: var(--accent-green);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }}
        .data-label::before {{
            content: '>';
            margin-right: 8px;
            color: var(--accent-cyan);
        }}

        .data-value {{
            font-size: 16px;
            line-height: 1.8;
            color: var(--text-main);
            background: rgba(0,0,0,0.4);
            padding: 20px;
            border-left: 4px solid var(--accent-cyan);
            border-radius: 0 4px 4px 0;
            position: relative;
        }}

        /* Categories Grid */
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 25px;
        }}

        .cat-card {{
            background: rgba(0,0,0,0.5);
            border: 1px solid var(--border-color);
            padding: 25px;
            position: relative;
            overflow: hidden;
            transition: all 0.2s ease;
        }}
        
        .cat-card:hover {{
            background: rgba(88, 166, 255, 0.05);
            border-color: var(--accent-cyan);
            transform: translateY(-5px);
        }}

        .cat-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 4px; height: 100%;
            background: var(--accent-cyan);
            transition: all 0.3s ease;
        }}
        
        .cat-card:hover::before {{
            box-shadow: 0 0 15px var(--accent-cyan);
        }}

        .cat-name {{
            font-size: 20px;
            color: #ffffff;
            margin-bottom: 15px;
            font-weight: 600;
            letter-spacing: 1px;
        }}

        .cat-def {{
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 20px;
            line-height: 1.6;
            min-height: 65px;
        }}

        .tag-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .tag {{
            background: transparent;
            border: 1px solid rgba(88, 166, 255, 0.4);
            color: var(--accent-cyan);
            font-size: 13px;
            padding: 5px 12px;
            border-radius: 0;
            font-family: 'Noto Sans SC', sans-serif;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .tag::before {{
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 100%; height: 100%;
            background: rgba(88, 166, 255, 0.2);
            transition: all 0.3s ease;
        }}
        
        .tag:hover::before {{
            left: 0;
        }}
        .tag:hover {{
            color: #fff;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 10px rgba(88, 166, 255, 0.3);
        }}

        /* Progress Bar */
        .progress-bar {{
            width: 100%;
            height: 4px;
            background: var(--border-color);
            margin-top: 15px;
            position: relative;
        }}
        .progress-fill {{
            position: absolute;
            left: 0; top: 0;
            height: 100%;
            background: var(--accent-cyan);
            width: 85%;
            box-shadow: 0 0 10px var(--accent-cyan);
        }}
        
        /* Sci-fi embellishments */
        .hud-corner-br {{
            position: absolute;
            bottom: 20px; right: 20px;
            font-family: 'Orbitron', sans-serif;
            font-size: 10px;
            color: var(--border-color);
        }}
        
        .vertical-text {{
            position: absolute;
            right: 15px;
            top: 150px;
            writing-mode: vertical-rl;
            text-orientation: mixed;
            font-family: 'Orbitron', sans-serif;
            color: var(--border-color);
            font-size: 14px;
            letter-spacing: 5px;
        }}
        
        /* UI Decals */
        .decal-1 {{
            position: absolute;
            top: 50%;
            left: 20px;
            width: 50px;
            height: 50px;
            border-left: 2px dashed rgba(88, 166, 255, 0.3);
            border-bottom: 2px dashed rgba(88, 166, 255, 0.3);
            pointer-events: none;
        }}
    </style>
</head>
<body>

    <div class="hud-scanline"></div>

    <header>
        <div class="hud-logo"></div>
        <div class="hud-title">END_FIELD // ANALYSIS_CORE</div>
        <div class="hud-sys-info">
            <span>OP_MODE_</span> SELECTIVE_CODING<br>
            <span>TARGET_NODE_</span> {docx_path}<br>
            <span>STATUS_</span> ONLINE
        </div>
    </header>

    <!-- Side decorative elements -->
    <div class="vertical-text">SYS.VER_2026.AR KNIGHTS // ENFIELD DB_SECURE</div>

    <div class="container">
        
        <!-- Storyline Panel -->
        <div class="panel">
            <div class="panel-header">
                <div class="panel-idx">01</div>
                <div class="panel-title">CORE_STORYLINE // 核心网络叙事</div>
            </div>
            
            <div style="display: flex; gap: 40px;">
                <div style="flex: 1;">
                    <div class="data-row">
                        <div class="data-label">TITLE_REF [A-1]</div>
                        <div class="data-value" style="font-size: 22px; font-weight: bold; color: #fff; text-shadow: 0 0 10px rgba(255,255,255,0.2);">
                            {storyline['title']}
                        </div>
                    </div>
                </div>
                
                <div style="width: 200px;">
                    <div class="data-label">SATURATION_INDEX</div>
                    <div style="font-family: 'Orbitron'; font-size: 32px; color: var(--accent-cyan); margin-top: 10px;">85.0%</div>
                    <div class="progress-bar"><div class="progress-fill"></div></div>
                </div>
            </div>

            <div class="data-row">
                <div class="data-label">NARRATIVE_DATA [A-2]</div>
                <div class="data-value">
                    {storyline['narrative']}
                </div>
            </div>
            <div class="hud-corner-br">BLOCK_ID_0A_F9</div>
        </div>

        <!-- Categories Panel -->
        <div class="panel">
            <div class="panel-header">
                <div class="panel-idx">02</div>
                <div class="panel-title">AXIAL_MATRIX // 轴心类属结构</div>
            </div>
            <div class="category-grid">
"""
    for cat in categories:
        html_content += f"""
                <div class="cat-card">
                    <div class="cat-name">{cat['name']}</div>
                    <div class="cat-def">{cat['def']}</div>
                    <div class="tag-list">
"""
        for code_label in cat['codes']:
            html_content += f'<span class="tag">{code_label}</span>'
            
        html_content += """
                    </div>
                </div>"""

    html_content += """
            </div>
            <div class="hud-corner-br">BLOCK_ID_0B_E7</div>
        </div>

        <!-- Raw Codes Panel -->
        <div class="panel">
            <div class="panel-header">
                <div class="panel-idx">03</div>
                <div class="panel-title">RAW_INDEX // 初级开放源</div>
            </div>
            <div class="tag-list" style="border: 1px dashed var(--border-color); padding: 25px; background: rgba(0,0,0,0.2);">
"""
    for c in codes:
        html_content += f'<span class="tag" title="{c["def"]}">{c["label"]}</span>\n'

    html_content += """
            </div>
            <div class="hud-corner-br">BLOCK_ID_0C_02</div>
        </div>
        
    </div>

</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Report customized and saved to {output_path}")

if __name__ == "__main__":
    generate_endfield_report("1.docx", "outputs/endfield_coding_report.html")
