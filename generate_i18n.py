#!/usr/bin/env python3
"""
Generate Chinese (zh) and Japanese (ja) versions of the Toolify site.
Reads English HTML files, applies translations, adds language switcher + hreflang.
"""
import os, re, copy

BASE = os.path.dirname(os.path.abspath(__file__))

# ---- Language switcher CSS (injected into <style>) ----
LANG_CSS = """
.lang-switcher{display:flex;gap:2px;align-items:center;margin-left:12px}
.lang-link{padding:4px 10px;border-radius:14px;font-size:12px;font-weight:600;color:var(--text-muted);text-decoration:none;transition:all .15s}
.lang-link:hover{background:var(--primary-light);color:var(--primary)}
.lang-link.active{background:var(--primary);color:#fff}
"""

def hreflang_tags(path):
    b = 'https://toolify.com'
    p = path.rstrip('/')
    en = f'{b}/{p}' if p else b
    zh = f'{b}/zh/{p}' if p else f'{b}/zh'
    ja = f'{b}/ja/{p}' if p else f'{b}/ja'
    return (f'<link rel="alternate" hreflang="en" href="{en}">\n'
            f'<link rel="alternate" hreflang="zh" href="{zh}">\n'
            f'<link rel="alternate" hreflang="ja" href="{ja}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{en}">')

def lang_switcher(path, current):
    def url(lang):
        if lang == 'en':
            return f'/{path}' if path else '/'
        return f'/{lang}/{path}' if path else f'/{lang}/'
    items = []
    for code, label in [('en','EN'),('zh','中文'),('ja','日本語')]:
        cls = 'lang-link active' if code == current else 'lang-link'
        items.append(f'<a href="{url(code)}" class="{cls}">{label}</a>')
    return '<div class="lang-switcher">' + ''.join(items) + '</div>'

# ============================================================
#  Translation pairs: (english, chinese, japanese)
#  Applied longest-first to avoid partial match issues.
# ============================================================

T = [
# ---- Shared: header nav ----
("All Tools", "全部工具", "すべてのツール"),
("How to Use", "使用方法", "使い方"),
("FAQ", "常见问题", "よくある質問"),

# ---- Shared: footer ----
("All tools run locally in your browser.", "所有工具均在浏览器本地运行。", "すべてのツールはブラウザ内でローカル実行されます。"),
("Privacy Policy", "隐私政策", "プライバシーポリシー"),
("Terms", "条款", "利用規約"),
("PDF to Word", "PDF转Word", "PDF to Word"),
("PDF Merge", "PDF合并", "PDF結合"),
("Compress PDF", "PDF压缩", "PDF圧縮"),
("JPG to PDF", "JPG转PDF", "JPG to PDF"),
("Word to PDF", "Word转PDF", "Word to PDF"),
("Image Compressor", "图片压缩", "画像圧縮"),
("QR Generator", "二维码生成", "QR生成"),

# ---- Ad placeholder ----
("[ AdSense Ad Unit — 728x90 ]", "[ 广告位 — 728x90 ]", "[ 広告枠 — 728x90 ]"),
("[ AdSense Ad Unit — 728×90 ]", "[ 广告位 — 728×90 ]", "[ 広告枠 — 728×90 ]"),

# ---- Badges ----
("No Upload", "无需上传", "アップロード不要"),
("No Signup", "无需注册", "登録不要"),
("No Watermark", "无水印", "透かしなし"),

# ---- PDF to Word: meta ----
("Free PDF to Word Converter — Convert PDF to DOCX Online Instantly",
 "免费PDF转Word转换器 — 在线即时将PDF转换为DOCX",
 "無料PDF to Word変換ツール — オンラインでPDFをDOCXに即時変換"),

("Convert PDF to editable Word (DOCX) online for free. No upload to any server — conversion happens right in your browser. Fast, private, no signup needed.",
 "免费在线将PDF转换为可编辑的Word (DOCX)文档。无需上传服务器—转换全部在浏览器中完成。快速、安全、无需注册。",
 "PDFを編集可能なWord（DOCX）に無料でオンライン変換。サーバーへのアップロード不要—変換はすべてブラウザ内で完結。高速、安全、登録不要。"),

("Free PDF to Word Converter — No Upload, Convert in Browser",
 "免费PDF转Word转换器 — 无需上传，浏览器内转换",
 "無料PDF to Word変換ツール — アップロード不要、ブラウザ内で変換"),

("Convert PDF to Word (DOCX) for free. No upload, no signup, completely private. All processing happens in your browser.",
 "免费将PDF转换为Word (DOCX)。无需上传、无需注册、完全隐私。所有处理在浏览器中完成。",
 "PDFをWord（DOCX）に無料変換。アップロード不要、登録不要、完全プライベート。すべての処理はブラウザ内で行われます。"),

# ---- PDF to Word: hero ----
("Free PDF to Word Converter",
 "免费PDF转Word转换器",
 "無料PDF to Word変換ツール"),

("Convert PDF to editable Word (DOCX) online — instantly and privately. No upload to any server, no signup, no watermarks. Your files stay on your device.",
 "在线将PDF转换为可编辑的Word (DOCX)文档—即时且安全。无需上传服务器，无需注册，无水印。文件始终保留在您的设备上。",
 "PDFを編集可能なWord（DOCX）にオンライン変換—即時かつ安全。サーバーアップロード不要、登録不要、透かしなし。ファイルはお使いのデバイスに残ります。"),

("Free & Instant", "免费即时", "無料＆即時"),

# ---- PDF to Word: upload ----
("Drop your PDF file here",
 "将PDF文件拖放到此处",
 "PDFファイルをここにドロップ"),

("Convert any PDF to an editable Word document — up to 50MB",
 "将任意PDF转换为可编辑的Word文档—最大50MB",
 "あらゆるPDFを編集可能なWord文書に変換—最大50MB"),

("or", "或", "または"),

("Browse Files", "选择文件", "ファイルを選択"),

# ---- PDF to Word: file preview ----
("Ready", "就绪", "準備完了"),
("Ready to convert", "准备转换", "変換準備完了"),

# ---- PDF to Word: warning ----
("Complex PDFs with heavy formatting, tables, or scanned images may not convert perfectly. For best results, use text-based PDFs. Scanned documents will be extracted as images in the Word file.",
 "包含复杂排版、表格或扫描图像的PDF可能无法完美转换。为获得最佳效果，请使用基于文本的PDF。扫描文档将以图片形式提取到Word文件中。",
 "複雑なフォーマット、表、スキャン画像を含むPDFは完全に変換できない場合があります。最適な結果にはテキストベースのPDFをご使用ください。スキャン文書はWordファイル内に画像として抽出されます。"),

# ---- PDF to Word: options ----
("Editable Document", "可编辑文档", "編集可能ドキュメント"),
("Extract text as editable content (recommended)", "提取文本为可编辑内容（推荐）", "テキストを編集可能なコンテンツとして抽出（推奨）"),
("Preserve Layout", "保留排版", "レイアウト保持"),
("Keep original formatting — larger file size", "保留原始格式—文件较大", "元のフォーマットを維持—ファイルサイズが大きくなります"),

# ---- PDF to Word: convert button ----
("Convert to Word", "转换为Word", "Wordに変換"),

# ---- PDF to Word: progress ----
("Analyzing PDF...", "正在分析PDF...", "PDFを分析中..."),
("Reading PDF...", "正在读取PDF...", "PDFを読み込み中..."),
("Extracting text content...", "正在提取文本内容...", "テキストを抽出中..."),
("Building Word document...", "正在生成Word文档...", "Word文書を生成中..."),
("Finalizing...", "正在完成...", "完了処理中..."),
("Done!", "完成！", "完了！"),
("Done", "完成", "完了"),

# ---- PDF to Word: result ----
("Conversion Complete!", "转换完成！", "変換完了！"),
("Your Word document is ready.", "您的Word文档已就绪。", "Word文書の準備ができました。"),
("Download Word File", "下载Word文件", "Wordファイルをダウンロード"),
("Convert Another File", "转换另一个文件", "別のファイルを変換"),

# ---- PDF to Word: SEO section ----
("How to Convert PDF to Word Online — Free & Private",
 "如何在线将PDF转换为Word—免费且安全",
 "PDFをWordにオンライン変換する方法—無料＆安全"),

("Upload Your PDF", "上传您的PDF", "PDFをアップロード"),
("Drag and drop or click to select your PDF file. Supports files up to 50MB.",
 "拖放或点击选择您的PDF文件。支持最大50MB的文件。",
 "ドラッグ＆ドロップまたはクリックしてPDFファイルを選択。最大50MBまで対応。"),

("Choose Mode", "选择模式", "モードを選択"),
('Select "Editable" for clean text or "Preserve Layout" to keep the original formatting.',
 '选择"可编辑"获取纯净文本，或选择"保留排版"保持原始格式。',
 '「編集可能」でクリーンなテキストを、「レイアウト保持」で元のフォーマットを維持。'),

("Convert & Download", "转换并下载", "変換＆ダウンロード"),
("Click convert — processing happens entirely in your browser. Download your DOCX instantly.",
 "点击转换—所有处理在浏览器中完成。即时下载DOCX文件。",
 "変換をクリック—処理はすべてブラウザ内で完結。DOCXを即時ダウンロード。"),

("What is PDF to Word Conversion?",
 "什么是PDF转Word转换？",
 "PDF to Word変換とは？"),

("PDF to Word conversion is the process of transforming a static PDF (Portable Document Format) file into an editable Microsoft Word (.docx) document. This allows you to modify text, adjust formatting, add or remove content, and repurpose the document — something that's not possible with a locked PDF. Our tool extracts text, images, and basic formatting from your PDF and reconstructs them in a Word-compatible format, all within your browser.",
 "PDF转Word转换是将静态PDF（便携文档格式）文件转换为可编辑的Microsoft Word (.docx)文档的过程。这使您可以修改文本、调整格式、添加或删除内容、重新利用文档—这些在锁定的PDF中无法实现。我们的工具从PDF中提取文本、图像和基本格式，并在浏览器中将其重建为Word兼容格式。",
 "PDF to Word変換とは、静的なPDF（Portable Document Format）ファイルを編集可能なMicrosoft Word（.docx）文書に変換するプロセスです。これにより、テキストの修正、フォーマットの調整、コンテンツの追加や削除、文書の再利用が可能になります—ロックされたPDFではできないことです。当ツールはPDFからテキスト、画像、基本フォーマットを抽出し、ブラウザ内でWord互換フォーマットに再構築します。"),

("Why Use Our Free PDF to Word Converter?",
 "为什么使用我们的免费PDF转Word转换器？",
 "当社の無料PDF to Word変換ツールを使う理由"),

("100% Private & Secure:", "100%隐私安全：", "100%プライベート＆安全："),
("Unlike other converters that upload your files to remote servers, our tool processes everything locally in your browser. Your confidential documents never leave your device.",
 "与其他将文件上传到远程服务器的转换器不同，我们的工具完全在浏览器本地处理。您的机密文档永远不会离开您的设备。",
 "他の変換ツールがファイルをリモートサーバーにアップロードするのとは異なり、当ツールはすべてブラウザ内でローカル処理します。機密文書がデバイスから外に出ることはありません。"),

("No Watermarks, No Limits:", "无水印，无限制：", "透かしなし、制限なし："),
('Many "free" converters add watermarks or restrict how many pages you can convert. We don\'t. Convert as many PDFs as you need, whenever you need.',
 '许多"免费"转换器会添加水印或限制转换页数。我们不会。随时转换任意数量的PDF。',
 '多くの「無料」変換ツールは透かしを追加したり変換ページ数を制限します。当ツールはしません。必要な時に必要なだけPDFを変換できます。'),

("No Signup Required:", "无需注册：", "登録不要："),
("Start converting immediately. No email, no account, no registration. Just upload and convert.",
 "立即开始转换。无需邮箱、无需账户、无需注册。上传即可转换。",
 "すぐに変換を開始。メール不要、アカウント不要、登録不要。アップロードして変換するだけ。"),

("Works on Any Device:", "支持所有设备：", "あらゆるデバイスで動作："),
("Desktop, laptop, tablet, or phone — our converter is fully responsive and works in any modern browser.",
 "台式机、笔记本、平板或手机—我们的转换器完全响应式，在任何现代浏览器中均可使用。",
 "デスクトップ、ノートPC、タブレット、スマートフォン—完全レスポンシブで、すべてのモダンブラウザで動作します。"),

("Instant Results:", "即时结果：", "即時結果："),
("Conversion takes seconds for most documents. No waiting for email delivery or queue processing.",
 "大多数文档转换只需几秒。无需等待邮件发送或队列处理。",
 "ほとんどの文書は数秒で変換完了。メール配信やキュー処理の待ち時間なし。"),

("Common Use Cases", "常见使用场景", "一般的なユースケース"),
("Edit Contracts & Agreements", "编辑合同与协议", "契約書・合意書の編集"),
("Convert signed PDF contracts into editable Word docs to make revisions, add clauses, or update terms.",
 "将已签署的PDF合同转换为可编辑的Word文档，进行修订、添加条款或更新条件。",
 "署名済みのPDF契約書を編集可能なWord文書に変換し、改訂、条項追加、条件更新を行えます。"),

("Update Your Resume", "更新您的简历", "履歴書の更新"),
("Have an old PDF resume? Convert it to Word and easily update your experience, skills, and formatting.",
 "有旧的PDF简历？转换为Word，轻松更新经历、技能和格式。",
 "古いPDF履歴書がありますか？Wordに変換して経歴、スキル、フォーマットを簡単に更新。"),

("Repurpose Reports & Research", "重新利用报告与研究", "報告書・研究の再利用"),
("Extract content from academic papers, reports, and research PDFs to quote, cite, or build upon.",
 "从学术论文、报告和研究PDF中提取内容，用于引用、参考或在此基础上扩展。",
 "学術論文、報告書、研究PDFからコンテンツを抽出し、引用、参照、発展させることができます。"),

("Fill Out Forms Digitally", "数字填写表格", "フォームのデジタル入力"),
("Convert PDF forms to Word, fill them out digitally, and save or print without handwriting.",
 "将PDF表格转换为Word，数字填写，保存或打印，无需手写。",
 "PDFフォームをWordに変換し、デジタルで入力、手書きなしで保存や印刷が可能。"),

("Translate Documents", "翻译文档", "文書の翻訳"),
("Convert PDF to Word, then use translation tools or AI to translate the content into another language.",
 "将PDF转换为Word，然后使用翻译工具或AI将内容翻译为其他语言。",
 "PDFをWordに変換し、翻訳ツールやAIでコンテンツを別の言語に翻訳。"),

("Extract Invoice Data", "提取发票数据", "請求書データの抽出"),
("Convert PDF invoices to Word to copy-paste data into accounting software or spreadsheets.",
 "将PDF发票转换为Word，复制粘贴数据到会计软件或电子表格。",
 "PDF請求書をWordに変換し、会計ソフトやスプレッドシートにデータをコピー＆ペースト。"),

("PDF to Word vs. Other Formats", "PDF转Word与其他格式对比", "PDF to Wordと他のフォーマットの比較"),
("While PDF to Word is the most popular conversion, you might also need:",
 "虽然PDF转Word是最常用的转换，您可能还需要：",
 "PDF to Wordは最も一般的な変換ですが、他にも以下が必要かもしれません："),

("PDF to Excel:", "PDF转Excel：", "PDF to Excel："),
("Best for tables, financial data, and spreadsheets embedded in PDFs.",
 "最适合PDF中嵌入的表格、财务数据和电子表格。",
 "PDFに埋め込まれた表、財務データ、スプレッドシートに最適。"),

("PDF to PowerPoint:", "PDF转PowerPoint：", "PDF to PowerPoint："),
("Convert presentation PDFs back into editable slides.",
 "将演示PDF转换回可编辑的幻灯片。",
 "プレゼンPDFを編集可能なスライドに変換。"),

("PDF to TXT:", "PDF转TXT：", "PDF to TXT："),
("Extract plain text only — useful for copy-pasting content without formatting.",
 "仅提取纯文本—适用于复制粘贴不带格式的内容。",
 "プレーンテキストのみ抽出—フォーマットなしでコンテンツをコピペするのに便利。"),

("PDF to Image (JPG/PNG):", "PDF转图片 (JPG/PNG)：", "PDF to Image (JPG/PNG)："),
("Convert each PDF page into a high-quality image file.",
 "将每个PDF页面转换为高质量图片文件。",
 "各PDFページを高品質な画像ファイルに変換。"),

("Frequently Asked Questions", "常见问题解答", "よくある質問"),
("Is this PDF to Word converter really free?",
 "这个PDF转Word转换器真的免费吗？",
 "このPDF to Word変換ツールは本当に無料ですか？"),

("Yes, completely free. No hidden costs, no subscription required, no watermarks on your output file. We sustain the tool through non-intrusive advertising on the page.",
 "是的，完全免费。无隐藏费用，无需订阅，输出文件无水印。我们通过页面上的非侵入式广告维持运营。",
 "はい、完全に無料です。隠れた費用なし、サブスク不要、出力ファイルに透かしなし。ページ上の控えめな広告で運営しています。"),

("Will my PDF formatting be preserved?",
 "我的PDF格式会被保留吗？",
 "PDFのフォーマットは保持されますか？"),

('Our "Preserve Layout" mode does its best to maintain fonts, spacing, tables, and images. However, highly complex PDFs (scanned documents, heavy graphics) may not convert perfectly. Text-based PDFs convert best.',
 '我们的"保留排版"模式会尽力保持字体、间距、表格和图像。但高度复杂的PDF（扫描文档、大量图形）可能无法完美转换。基于文本的PDF转换效果最佳。',
 '「レイアウト保持」モードはフォント、間隔、表、画像の維持に最善を尽くします。ただし、複雑なPDF（スキャン文書、重いグラフィック）は完全に変換できない場合があります。テキストベースのPDFが最も良好に変換されます。'),

("Is it safe to convert sensitive documents?",
 "转换敏感文档安全吗？",
 "機密文書の変換は安全ですか？"),

("Absolutely. All conversion happens locally in your browser. Your files are never uploaded to any server — they never leave your computer. This makes our tool ideal for confidential contracts, legal documents, and personal files.",
 "绝对安全。所有转换在浏览器本地完成。您的文件永远不会上传到任何服务器—永远不会离开您的电脑。这使我们的工具非常适合机密合同、法律文件和个人文件。",
 "はい。すべての変換はブラウザ内でローカルに行われます。ファイルはサーバーにアップロードされず、お使いのコンピュータから出ることはありません。機密契約書、法的文書、個人ファイルに最適です。"),

("Can I convert scanned PDFs (image-based)?",
 "可以转换扫描PDF（基于图像）吗？",
 "スキャンPDF（画像ベース）を変換できますか？"),

("Our tool extracts images from scanned PDFs and places them in the Word document. For full OCR (optical character recognition) that converts scanned images into editable text, you may need a dedicated OCR tool — we're working on adding this feature.",
 "我们的工具从扫描PDF中提取图像并放入Word文档。对于将扫描图像转换为可编辑文本的完整OCR（光学字符识别），您可能需要专门的OCR工具—我们正在开发此功能。",
 "当ツールはスキャンPDFから画像を抽出し、Word文書に配置します。スキャン画像を編集可能なテキストに変換する完全なOCR（光学式文字認識）には専用ツールが必要な場合があります—この機能の追加を開発中です。"),

("What's the maximum file size?",
 "最大文件大小是多少？",
 "最大ファイルサイズは？"),

("We recommend files up to 50MB for the best experience. Since processing happens in your browser, larger files may be slower depending on your device's performance and available memory.",
 "建议使用50MB以下的文件以获得最佳体验。由于处理在浏览器中进行，较大文件可能较慢，具体取决于设备性能和可用内存。",
 "最適な体験には50MB以下のファイルを推奨します。処理はブラウザ内で行われるため、大きいファイルはデバイスの性能とメモリによって遅くなる場合があります。"),

("Does it work on mobile phones?",
 "在手机上能用吗？",
 "スマートフォンで動作しますか？"),

("Yes! Our converter works on iOS, Android, and any modern mobile browser. You can convert PDFs to Word directly on your phone or tablet.",
 "可以！我们的转换器支持iOS、Android和任何现代移动浏览器。您可以直接在手机或平板上将PDF转换为Word。",
 "はい！iOS、Android、すべてのモダンモバイルブラウザで動作します。スマートフォンやタブレットで直接PDFをWordに変換できます。"),

("Can I convert password-protected PDFs?",
 "可以转换受密码保护的PDF吗？",
 "パスワード保護されたPDFを変換できますか？"),

("No, you'll need to remove the password first. Use our free PDF Unlock tool to remove password protection, then come back to convert.",
 "不可以，您需要先移除密码。使用我们的免费PDF解锁工具移除密码保护，然后再来转换。",
 "いいえ、まずパスワードを解除する必要があります。無料のPDFロック解除ツールでパスワード保護を解除してから変換してください。"),

("What's the difference between this and Adobe Acrobat?",
 "这和Adobe Acrobat有什么区别？",
 "これはAdobe Acrobatとどう違いますか？"),

("Adobe Acrobat Pro costs $19.99/month. Our tool is completely free and works in your browser without installing anything. For basic PDF to Word conversion, our tool handles most use cases perfectly.",
 "Adobe Acrobat Pro每月$19.99。我们的工具完全免费，在浏览器中运行，无需安装。对于基本的PDF转Word转换，我们的工具能完美处理大多数场景。",
 "Adobe Acrobat Proは月額$19.99です。当ツールは完全無料で、ブラウザで動作、インストール不要。基本的なPDF to Word変換において、ほとんどのユースケースを完璧に処理します。"),

# ---- PDF to Word: JS strings ----
("Please select a PDF file.", "请选择PDF文件。", "PDFファイルを選択してください。"),
("File too large. Please use a PDF under 50MB.", "文件过大。请使用50MB以下的PDF。", "ファイルが大きすぎます。50MB以下のPDFをご使用ください。"),
("Conversion failed. ", "转换失败。", "変換に失敗しました。"),
("No extractable text found. This PDF may be scanned (image-based). For scanned documents, an OCR tool is needed.",
 "未找到可提取的文本。此PDF可能是扫描件（基于图像）。扫描文档需要OCR工具。",
 "抽出可能なテキストが見つかりません。このPDFはスキャン（画像ベース）の可能性があります。スキャン文書にはOCRツールが必要です。"),
("This PDF is password-protected. Please unlock it first.",
 "此PDF受密码保护。请先解锁。",
 "このPDFはパスワード保護されています。まずロックを解除してください。"),
("The file appears to be corrupted or not a valid PDF.",
 "文件似乎已损坏或不是有效的PDF。",
 "ファイルが破損しているか、有効なPDFではないようです。"),
("Please try a different PDF file.", "请尝试其他PDF文件。", "別のPDFファイルをお試しください。"),
("Conversion complete!", "转换完成！", "変換完了！"),
("Converted from PDF", "从PDF转换", "PDFから変換"),
("page", "页", "ページ"),
("pages", "页", "ページ"),
("Extracting page", "正在提取第", "ページを抽出中"),
("of", "共", "/"),
("Converted with Toolify — Free Online PDF to Word Converter",
 "由Toolify转换 — 免费在线PDF转Word转换器",
 "Toolifyで変換 — 無料オンラインPDF to Word変換ツール"),

# ---- PDF to Word: structured data ----
("Convert PDF to editable Word (DOCX) online for free. No upload required — conversion happens entirely in your browser. Fast, private, no signup.",
 "免费在线将PDF转换为可编辑的Word (DOCX)。无需上传—转换全部在浏览器中完成。快速、安全、无需注册。",
 "PDFを編集可能なWord（DOCX）に無料でオンライン変換。アップロード不要—変換はすべてブラウザ内で完結。高速、安全、登録不要。"),

# ============================================================
#  PDF Merge page
# ============================================================

("Free Online PDF Merger — Merge PDFs in Browser, No Upload",
 "免费在线PDF合并工具 — 浏览器内合并，无需上传",
 "無料オンラインPDF結合ツール — ブラウザ内で結合、アップロード不要"),

("Merge PDF files online for free. No upload required — all processing happens in your browser. Combine multiple PDFs into one, reorder pages, fast and secure.",
 "免费在线合并PDF文件。无需上传—所有处理在浏览器中完成。合并多个PDF为一个，调整顺序，快速安全。",
 "PDFファイルを無料でオンライン結合。アップロード不要—すべての処理はブラウザ内で完結。複数のPDFを1つに結合、並べ替え、高速・安全。"),

("Free Online PDF Merger — No Upload, Merge in Browser",
 "免费在线PDF合并工具 — 无需上传，浏览器内合并",
 "無料オンラインPDF結合ツール — アップロード不要、ブラウザ内で結合"),

("Merge PDF files online for free. No upload, no signup, completely private. All processing happens in your browser.",
 "免费在线合并PDF文件。无需上传、无需注册、完全隐私。所有处理在浏览器中完成。",
 "PDFファイルを無料でオンライン結合。アップロード不要、登録不要、完全プライベート。すべての処理はブラウザ内で行われます。"),

("Free Online PDF Merger",
 "免费在线PDF合并工具",
 "無料オンラインPDF結合ツール"),

("Merge multiple PDF files into one — right in your browser. No upload, no signup, no watermarks. Drag to reorder, click to merge.",
 "在浏览器中合并多个PDF文件为一个。无需上传、无需注册、无水印。拖拽排序，点击合并。",
 "ブラウザ内で複数のPDFファイルを1つに結合。アップロード不要、登録不要、透かしなし。ドラッグで並べ替え、クリックで結合。"),

("Fast & Free", "快速免费", "高速＆無料"),

("Drop PDF files here to merge",
 "将PDF文件拖放到此处合并",
 "結合するPDFファイルをここにドロップ"),

("Select 2 or more PDF files — up to 50MB each",
 "选择2个或更多PDF文件—每个最大50MB",
 "2つ以上のPDFファイルを選択—各最大50MB"),

("+ Add More", "+ 添加更多", "+ 追加"),

("Files to Merge", "待合并文件", "結合するファイル"),
("Drag files to reorder. Files will be merged top to bottom.",
 "拖拽文件排序。文件将从上到下合并。",
 "ドラッグで並べ替え。上から下の順に結合されます。"),

("Merge PDFs", "合并PDF", "PDFを結合"),
("Merging...", "正在合并...", "結合中..."),
("Merge Complete!", "合并完成！", "結合完了！"),
("Your merged PDF is ready.", "您合并的PDF已就绪。", "結合されたPDFの準備ができました。"),
("Download Merged PDF", "下载合并的PDF", "結合PDFをダウンロード"),
("Start Over", "重新开始", "最初から"),

("How to Merge PDF Files Online — Free & Private",
 "如何在线合并PDF文件—免费且安全",
 "PDFファイルをオンライン結合する方法—無料＆安全"),

("Upload PDFs", "上传PDF", "PDFをアップロード"),
("Drag and drop or browse to select multiple PDF files you want to combine.",
 "拖放或浏览选择要合并的多个PDF文件。",
 "ドラッグ＆ドロップまたはブラウズで結合する複数のPDFファイルを選択。"),

("Reorder", "排序", "並べ替え"),
("Drag files up or down to set the merge order. The top file comes first in the result.",
 "上下拖拽文件设置合并顺序。顶部文件在结果中排第一。",
 "ファイルを上下にドラッグして結合順を設定。一番上のファイルが結果の最初になります。"),

("Merge & Download", "合并并下载", "結合＆ダウンロード"),
("Click merge — combining happens entirely in your browser. Download instantly.",
 "点击合并—合并在浏览器中完全完成。即时下载。",
 "結合をクリック—処理はすべてブラウザ内で完結。即時ダウンロード。"),

("What is PDF Merging?",
 "什么是PDF合并？",
 "PDF結合とは？"),

("PDF merging (also called combining or concatenating) is the process of joining multiple PDF files into a single document. Instead of opening and reading several files one by one, you combine them into one cohesive PDF — perfect for reports, portfolios, contracts, and presentations. Our tool performs this operation entirely in your browser, so your files never leave your device.",
 "PDF合并（也称组合或连接）是将多个PDF文件合并为单个文档的过程。您可以将多个文件合并为一个完整的PDF，而非逐个打开阅读—非常适合报告、作品集、合同和演示文稿。我们的工具完全在浏览器中执行此操作，文件永远不会离开您的设备。",
 "PDF結合（結合または連結とも呼ばれる）は、複数のPDFファイルを1つの文書に統合するプロセスです。複数のファイルを1つにまとめることで、個別に開く必要がなくなり、報告書、ポートフォリオ、契約書、プレゼンに最適です。当ツールはすべてブラウザ内で実行するため、ファイルがデバイスから外に出ることはありません。"),

("Why Use Our Free PDF Merger?",
 "为什么使用我们的免费PDF合并工具？",
 "当社の無料PDF結合ツールを使う理由"),

("No Limits:", "无限制：", "制限なし："),
("Merge as many PDFs as you want. No daily limits, no page restrictions, no file count caps.",
 "合并任意数量的PDF。无每日限制、无页数限制、无文件数量上限。",
 "好きなだけPDFを結合。1日の制限なし、ページ制限なし、ファイル数上限なし。"),

("Drag to Reorder:", "拖拽排序：", "ドラッグで並べ替え："),
("Easily rearrange the merge order by dragging files up or down in the list. The order you see is the order you get.",
 "通过上下拖拽列表中的文件轻松调整合并顺序。所见即所得。",
 "リスト内のファイルを上下にドラッグして結合順を簡単に調整。見た目通りに結合されます。"),

("No Watermarks:", "无水印：", "透かしなし："),
("The merged PDF is clean — no branding, no watermarks, no ads embedded in your document.",
 "合并的PDF干净整洁—无品牌标识、无水印、文档内无嵌入广告。",
 "結合されたPDFはクリーン—ブランドマークなし、透かしなし、文書内に広告なし。"),

("Works Everywhere:", "全平台支持：", "どこでも動作："),
("Desktop, tablet, or phone — our merger works on any device with a modern browser.",
 "台式机、平板或手机—我们的合并工具支持任何具有现代浏览器的设备。",
 "デスクトップ、タブレット、スマートフォン—モダンブラウザを搭載するあらゆるデバイスで動作。"),

("Common Use Cases", "常见使用场景", "一般的なユースケース"),
("Combine contracts:", "合并合同：", "契約書の結合："),
("Merge a main contract with appendices, terms, and signature pages into one file.",
 "将主合同与附录、条款和签名页合并为一个文件。",
 "主契約書と付録、条項、署名ページを1つのファイルに結合。"),

("Assemble reports:", "组装报告：", "報告書の作成："),
("Combine cover pages, executive summaries, and individual sections into a single report.",
 "将封面、执行摘要和各个章节合并为单个报告。",
 "表紙、エグゼクティブサマリー、各セクションを1つの報告書に結合。"),

("Portfolio creation:", "作品集创建：", "ポートフォリオ作成："),
("Merge certificates, work samples, and cover letters into one portfolio PDF.",
 "将证书、作品样本和求职信合并为一个作品集PDF。",
 "証明書、作品サンプル、カバーレターを1つのポートフォリオPDFに結合。"),

("Invoice bundling:", "发票打包：", "請求書の束ね："),
("Combine monthly invoices into one file for accounting or client submissions.",
 "将月度发票合并为一个文件，用于会计或客户提交。",
 "月次請求書を1つのファイルにまとめて会計や顧客提出に。"),

("Course materials:", "课程材料：", "コース資料："),
("Merge lecture notes, slides, and readings into one study packet.",
 "将讲义、幻灯片和阅读材料合并为一个学习包。",
 "講義ノート、スライド、リーディングを1つの学習パケットに結合。"),

("Frequently Asked Questions", "常见问题解答", "よくある質問"),
("Is this PDF merger really free?",
 "这个PDF合并工具真的免费吗？",
 "このPDF結合ツールは本当に無料ですか？"),

("Yes, completely free with no limits. We sustain the tool through non-intrusive advertising on the page.",
 "是的，完全免费且无限制。我们通过页面上的非侵入式广告维持运营。",
 "はい、完全に無料で制限なし。ページ上の控えめな広告で運営しています。"),

("How many PDFs can I merge at once?",
 "一次可以合并多少个PDF？",
 "一度にいくつのPDFを結合できますか？"),

("There's no hard limit. However, since processing happens in your browser, very large numbers of files or very large files may be slow depending on your device's memory.",
 "没有硬性限制。但由于处理在浏览器中进行，大量文件或大文件可能较慢，具体取决于设备内存。",
 "ハードリミットはありません。ただし処理はブラウザ内で行われるため、非常に多くのファイルや大きなファイルはデバイスのメモリによって遅くなる場合があります。"),

("Are my files uploaded to a server?",
 "我的文件会上传到服务器吗？",
 "ファイルはサーバーにアップロードされますか？"),

("No. All merging happens locally in your browser using JavaScript. Your files never leave your device, making this safe for confidential documents.",
 "不会。所有合并在浏览器中使用JavaScript本地完成。文件永远不会离开您的设备，适合机密文档。",
 "いいえ。すべての結合はJavaScriptでブラウザ内でローカルに行われます。ファイルがデバイスから出ることはなく、機密文書にも安全です。"),

("Can I reorder pages within a single PDF?",
 "可以在单个PDF内重新排序页面吗？",
 "1つのPDF内のページを並べ替えできますか？"),

("This tool merges entire files. For reordering individual pages within a PDF, try our PDF Page Reorder tool (coming soon).",
 "此工具合并整个文件。如需在PDF内重新排序单个页面，请使用我们的PDF页面排序工具（即将推出）。",
 "このツールはファイル全体を結合します。PDF内の個別ページの並べ替えにはPDFページ並べ替えツール（近日公開）をお試しください。"),

("What's the maximum file size?",
 "最大文件大小是多少？", "最大ファイルサイズは？"),

("We recommend files up to 50MB each. Since merging happens in your browser, available memory is the limiting factor.",
 "建议每个文件50MB以下。由于合并在浏览器中进行，可用内存是限制因素。",
 "各50MB以下を推奨。結合はブラウザ内で行われるため、利用可能メモリが制限要因です。"),

("Does it work on mobile?",
 "在手机上能用吗？", "スマートフォンで動作しますか？"),

("Yes! Our merger works on iOS, Android, and any modern mobile browser.",
 "可以！我们的合并工具支持iOS、Android和任何现代移动浏览器。",
 "はい！iOS、Android、すべてのモダンモバイルブラウザで動作します。"),

("Will the quality be affected?",
 "质量会受影响吗？", "品質は影響を受けますか？"),

("No. Merging simply concatenates the PDF data — no re-encoding or compression is applied. Your pages look exactly as they did in the original files.",
 "不会。合并只是连接PDF数据—不进行重新编码或压缩。您的页面与原始文件完全一致。",
 "いいえ。結合はPDFデータを連結するだけ—再エンコードや圧縮は行われません。ページは元のファイルと全く同じように見えます。"),

# ---- PDF Merge: JS strings ----
("Please add at least 2 PDF files to merge.", "请至少添加2个PDF文件进行合并。", "結合には少なくとも2つのPDFファイルを追加してください。"),
("No valid PDF files found.", "未找到有效的PDF文件。", "有効なPDFファイルが見つかりません。"),
("file", "个文件", "ファイル"),  # careful
("files added", "个文件已添加", "ファイルを追加しました"),
("file added", "个文件已添加", "ファイルを追加しました"),
("is over 50MB, skipped.", "超过50MB，已跳过。", "は50MBを超えているためスキップしました。"),
("Merge failed. ", "合并失败。", "結合に失敗しました。"),
("One of the PDFs is password-protected. Please unlock it first.",
 "其中一个PDF受密码保护。请先解锁。",
 "いずれかのPDFがパスワード保護されています。まずロックを解除してください。"),
("One of the files appears to be corrupted.",
 "其中一个文件似乎已损坏。",
 "いずれかのファイルが破損しているようです。"),
("Please check your files and try again.", "请检查文件后重试。", "ファイルを確認してもう一度お試しください。"),
("Merge complete!", "合并完成！", "結合完了！"),
("Merged", "已合并", "結合済み"),
("PDFs into one file with", "个PDF为一个文件，共", "つのPDFを1つのファイルに結合、"),
("Finalizing merged PDF...", "正在完成合并...", "結合PDFを完成中..."),
("Processing", "正在处理", "処理中"),

# ============================================================
#  Landing page
# ============================================================

("Toolify — Free Online Tools | PDF, Image, Text Utilities",
 "Toolify — 免费在线工具 | PDF、图片、文本工具",
 "Toolify — 無料オンラインツール | PDF、画像、テキストユーティリティ"),

("Toolify offers free online tools that run entirely in your browser — PDF merger, PDF to Word converter, image compressor, and more. No upload, no signup, no watermarks.",
 "Toolify提供完全在浏览器中运行的免费在线工具—PDF合并、PDF转Word、图片压缩等。无需上传、无需注册、无水印。",
 "Toolifyはブラウザ内で完全に動作する無料オンラインツールを提供—PDF結合、PDF to Word変換、画像圧縮など。アップロード不要、登録不要、透かしなし。"),

("Toolify — Free Online Tools", "Toolify — 免费在线工具", "Toolify — 無料オンラインツール"),
("Free online tools that run in your browser. No upload, no signup, no watermarks.",
 "在浏览器中运行的免费在线工具。无需上传、无需注册、无水印。",
 "ブラウザで動作する無料オンラインツール。アップロード不要、登録不要、透かしなし。"),

("Free Online Tools", "免费在线工具", "無料オンラインツール"),
("Powerful utilities that run entirely in your browser. No uploads, no signups, no watermarks. Your files never leave your device.",
 "完全在浏览器中运行的强大工具。无需上传、无需注册、无水印。文件永远不会离开您的设备。",
 "ブラウザ内で完全に動作する強力なユーティリティ。アップロード不要、登録不要、透かしなし。ファイルはデバイスから出ません。"),

("100% Private", "100%隐私", "100%プライベート"),
("Instant", "即时", "即時"),
("Free Forever", "永久免费", "永久無料"),

("All Tools", "全部工具", "すべてのツール"),
("Browse our growing collection of free browser-based utilities",
 "浏览我们不断增长的免费浏览器工具集",
 "無料のブラウザベースユーティリティのコレクションをご覧ください"),

("Convert PDF files to editable Word (DOCX) documents. Real text extraction, right in your browser.",
 "将PDF文件转换为可编辑的Word (DOCX)文档。在浏览器中进行真实文本提取。",
 "PDFファイルを編集可能なWord（DOCX）文書に変換。ブラウザ内で実際のテキスト抽出。"),

("Combine multiple PDF files into one. Drag to reorder, click to merge. No upload required.",
 "合并多个PDF文件为一个。拖拽排序，点击合并。无需上传。",
 "複数のPDFファイルを1つに結合。ドラッグで並べ替え、クリックで結合。アップロード不要。"),

("Available", "可用", "利用可能"),
("Coming Soon", "即将推出", "近日公開"),

("Reduce PDF file size while maintaining quality. Perfect for email attachments and web uploads.",
 "在保持质量的同时减小PDF文件大小。非常适合邮件附件和网页上传。",
 "品質を維持しながらPDFファイルサイズを縮小。メール添付やウェブアップロードに最適。"),

("PDF Split", "PDF拆分", "PDF分割"),
("Split a PDF into individual pages or page ranges. Extract exactly what you need.",
 "将PDF拆分为单个页面或页面范围。精确提取所需内容。",
 "PDFを個別ページまたはページ範囲に分割。必要なものを正確に抽出。"),

("PDF to JPG", "PDF转JPG", "PDF to JPG"),
("Convert each PDF page into a high-quality JPG image. Great for thumbnails and previews.",
 "将每个PDF页面转换为高质量JPG图片。适合缩略图和预览。",
 "各PDFページを高品質JPG画像に変換。サムネイルやプレビューに最適。"),

("Combine multiple images into a single PDF document. Supports JPG, PNG, and WebP.",
 "将多张图片合并为单个PDF文档。支持JPG、PNG和WebP。",
 "複数の画像を1つのPDF文書に結合。JPG、PNG、WebPに対応。"),

("Image Resizer", "图片缩放", "画像リサイズ"),
("Resize images to exact dimensions or percentage. Batch process multiple files at once.",
 "将图片调整为精确尺寸或百分比。批量处理多个文件。",
 "画像を正確なサイズまたはパーセンテージにリサイズ。複数ファイルを一括処理。"),

("Word Counter", "字数统计", "文字数カウンター"),
("Count words, characters, sentences, and paragraphs. Reading time estimation included.",
 "统计单词、字符、句子和段落数。包含阅读时间估算。",
 "単語、文字、文、段落をカウント。読了時間の見積もり付き。"),

("JSON Formatter", "JSON格式化", "JSONフォーマッター"),
("Format, validate, and minify JSON data. Syntax highlighting and tree view.",
 "格式化、验证和压缩JSON数据。语法高亮和树形视图。",
 "JSONデータのフォーマット、検証、圧縮。シンタックスハイライトとツリービュー。"),

("Why Toolify?", "为什么选择Toolify？", "Toolifyを選ぶ理由？"),
("Privacy-first tools that just work", "隐私优先，开箱即用的工具", "プライバシー優先、すぐに使えるツール"),

("Files Never Leave", "文件不离设备", "ファイルは外部に送信されません"),
("All processing happens in your browser. No uploads, no servers, no tracking of your documents.",
 "所有处理在浏览器中完成。无需上传、无需服务器、不跟踪您的文档。",
 "すべての処理はブラウザ内で完結。アップロード不要、サーバー不要、文書の追跡なし。"),

("Lightning Fast", "闪电速度", "超高速"),
("No waiting in queues. No email delivery. Results are ready the instant processing completes.",
 "无需排队等待。无需邮件发送。处理完成即出结果。",
 "待ち行列なし。メール配信なし。処理完了と同時に結果表示。"),

("No Account Needed", "无需账户", "アカウント不要"),
("No signup, no login, no email required. Open the page and start using — that's it.",
 "无需注册、登录或邮箱。打开页面即可使用—就这么简单。",
 "登録、ログイン、メール不要。ページを開いてすぐ使える—それだけ。"),

("Your output files are clean. No branding, no ads embedded in your documents, no strings attached.",
 "输出文件干净整洁。无品牌标识、无嵌入广告、无任何附加条件。",
 "出力ファイルはクリーン。ブランドマークなし、文書内広告なし、条件なし。"),

# ---- Landing: tool categories ----
("Compress PDF", "PDF压缩", "PDF圧縮"),
("Image Compressor", "图片压缩", "画像圧縮"),

# ---- Nav: Pricing & Support ----
("Pricing", "定价", "料金"),
("Support", "支持", "サポート"),

# ---- Pricing page ----
("Pricing — Toolify Premium | Unlock Unlimited Tools",
 "定价 — Toolify高级 | 解锁无限工具",
 "料金 — Toolifyプレミアム | 無制限ツールをアンロック"),
("Upgrade to Toolify Premium for just $9.99/month. Unlimited PDF conversions, no ads, 50MB file limit, and priority processing. Cancel anytime.",
 "升级到Toolify高级，每月仅需$9.99。无限PDF转换，无广告，50MB文件限制，优先处理。随时取消。",
 "Toolifyプレミアムにアップグレード、月額$9.99のみ。無制限PDF変換、広告なし、50MBファイル制限、優先処理。いつでもキャンセル。"),
("Toolify Pricing — Premium for $9.99/month",
 "Toolify定价 — 高级会员$9.99/月",
 "Toolify料金 — プレミアム$9.99/月"),
("Unlock unlimited PDF tools, no ads, and priority processing. Just $9.99/month.",
 "解锁无限PDF工具，无广告，优先处理。每月仅需$9.99。",
 "無制限のPDFツール、広告なし、優先処理をアンロック。月額$9.99のみ。"),
("Simple, Transparent Pricing",
 "简单透明的定价",
 "シンプルで透明な料金"),
("Start free forever. Upgrade when you need more power. Cancel anytime.",
 "永久免费开始。需要更多功能时升级。随时取消。",
 "永久無料で開始。必要な時にアップグレード。いつでもキャンセル。"),
("Most Popular", "最受欢迎", "人気No.1"),
("Get Started Free", "免费开始", "無料で開始"),
("Upgrade to Premium", "升级到高级", "プレミアムにアップグレード"),
("Cancel anytime. Secure payment by Lemon Squeezy.",
 "随时取消。由Lemon Squeezy安全支付。",
 "いつでもキャンセル。Lemon Squeezyによる安全な決済。"),
("Feature Comparison", "功能对比", "機能比較"),
("Feature", "功能", "機能"),
("3 merges / 3 conversions per day", "每天3次合并/3次转换", "1日3回の結合/3回の変換"),
("Up to 10MB per file", "每个文件最大10MB", "ファイルあたり最大10MB"),
("All tools included", "包含所有工具", "すべてのツール含む"),
("Browser-based, no upload", "浏览器端运行，无需上传", "ブラウザベース、アップロード不要"),
("No ads", "无广告", "広告なし"),
("Priority processing", "优先处理", "優先処理"),
("Unlimited merges & conversions", "无限合并和转换", "無制限の結合と変換"),
("Up to 50MB per file", "每个文件最大50MB", "ファイルあたり最大50MB"),
("No ads, ever", "永远无广告", "広告なし、永遠に"),
("Email support", "邮件支持", "メールサポート"),
("Pricing FAQ", "定价常见问题", "料金FAQ"),

# ---- Support page ----
("Support & Help — Toolify | Contact Us",
 "支持与帮助 — Toolify | 联系我们",
 "サポート＆ヘルプ — Toolify | お問い合わせ"),
("Get help with Toolify tools. Contact our support team by email, browse FAQs, and find answers to common questions about PDF conversion and merging.",
 "获取Toolify工具帮助。通过邮件联系我们的支持团队，浏览常见问题，找到关于PDF转换和合并的答案。",
 "Toolifyツールのヘルプ。メールでサポートチームにお問い合わせ、FAQを閲覧、PDF変換と結合に関するよくある質問の回答を見つけよう。"),
("Toolify Support & Help", "Toolify支持与帮助", "Toolifyサポート＆ヘルプ"),
("Contact our support team by email and browse FAQs.",
 "通过邮件联系我们的支持团队并浏览常见问题。",
 "メールでサポートチームにお問い合わせいただき、FAQをご覧ください。"),
("Support & Help", "支持与帮助", "サポート＆ヘルプ"),
("Need help? We are here for you. Browse our FAQ or send us an email.",
 "需要帮助？我们在这里。浏览常见问题或给我们发邮件。",
 "お困りですか？ここにいます。FAQをご覧いただくか、メールでお問い合わせください。"),
("Email Us", "给我们发邮件", "メールでお問い合わせ"),
("Have a question, bug report, or feature request? Send us an email and we will get back to you within 24 hours.",
 "有问题、bug报告或功能建议？给我们发邮件，我们将在24小时内回复。",
 "ご質問、バグ報告、機能リクエストがありますか？メールをお送りください。24時間以内にご返信します。"),

# ---- Currency Converter page ----
("Free Currency Exchange Rate Converter — Real-Time USD Rates",
 "免费汇率换算器 — 实时美元汇率",
 "無料為替レート変換ツール — リアルタイムUSDレート"),
("Convert currencies with real-time exchange rates. USD-based converter supporting 160+ currencies. Free, no signup, updated every minute.",
 "使用实时汇率换算货币。基于美元的换算器，支持160+种货币。免费、无需注册、每分钟更新。",
 "リアルタイム為替レートで通貨を変換。USDベース、160以上の通貨に対応。無料、登録不要、毎分更新。"),
("Free Currency Exchange Rate Converter — Real-Time Rates",
 "免费汇率换算器 — 实时汇率",
 "無料為替レート変換ツール — リアルタイムレート"),
("Convert currencies with real-time exchange rates. USD-based, 160+ currencies supported.",
 "使用实时汇率换算货币。基于美元，支持160+种货币。",
 "リアルタイム為替レートで通貨を変換。USDベース、160以上の通貨に対応。"),
("Free Currency Exchange Rate Converter",
 "免费汇率换算器",
 "無料為替レート変換ツール"),
("Real-time exchange rates for 160+ currencies. USD-based, updated every minute. Convert money instantly — no signup, completely free.",
 "160+种货币的实时汇率。基于美元，每分钟更新。即时换算—无需注册，完全免费。",
 "160以上の通貨のリアルタイムレート。USDベース、毎分更新。即時変換—登録不要、完全無料。"),
("Real-Time Rates", "实时汇率", "リアルタイムレート"),
("160+ Currencies", "160+种货币", "160+通貨"),
("Amount", "金额", "金額"),
("From", "从", "変換元"),
("1 USD = Popular Exchange Rates", "1美元 = 热门汇率", "1 USD = 人気為替レート"),
("1 USD buys", "1美元可兑", "1 USDで購入可能"),
("Loading exchange rates...", "正在加载汇率...", "為替レートを読み込み中..."),
("Fetching latest rates...", "正在获取最新汇率...", "最新レートを取得中..."),
("Using cached rates (offline mode)", "使用缓存汇率（离线模式）", "キャッシュレートを使用中（オフラインモード）"),
("Live rates unavailable. Showing cached rates.", "实时汇率不可用。显示缓存汇率。", "ライブレートが利用できません。キャッシュレートを表示しています。"),
("How to Use the Currency Converter", "如何使用汇率换算器", "為替レート変換ツールの使い方"),
("Exchange rates for reference only.", "汇率仅供参考。", "為替レートは参考用です。"),
("Currency Converter", "汇率换算", "為替レート変換"),

# ---- PDF Split page ----
("Free PDF Splitter — Split PDF Online, No Upload",
 "免费PDF拆分工具 — 在线拆分PDF，无需上传",
 "無料PDF分割ツール — オンラインでPDFを分割、アップロード不要"),
("Split PDF files online for free. Extract specific pages or split into individual files. No upload — all processing in your browser. Fast, private, no signup.",
 "免费在线拆分PDF文件。提取特定页面或拆分为单个文件。无需上传—所有处理在浏览器中完成。快速、安全、无需注册。",
 "PDFファイルを無料でオンライン分割。特定ページの抽出または個別ファイルへの分割。アップロード不要—すべての処理はブラウザ内で完結。高速、安全、登録不要。"),
("Free PDF Splitter — No Upload, Split in Browser",
 "免费PDF拆分工具 — 无需上传，浏览器内拆分",
 "無料PDF分割ツール — アップロード不要、ブラウザ内で分割"),
("Split PDF files online for free. Extract pages, split by ranges. No upload, no signup, completely private.",
 "免费在线拆分PDF文件。提取页面，按范围拆分。无需上传、无需注册、完全隐私。",
 "PDFファイルを無料でオンライン分割。ページ抽出、範囲指定分割。アップロード不要、登録不要、完全プライベート。"),
("Free PDF Splitter",
 "免费PDF拆分工具",
 "無料PDF分割ツール"),
("Split PDF files into smaller parts — extract specific pages or split into individual files. All processing in your browser, no upload, completely private.",
 "将PDF文件拆分为更小的部分—提取特定页面或拆分为单个文件。所有处理在浏览器中完成，无需上传，完全隐私。",
 "PDFファイルをより小さな部分に分割—特定ページの抽出または個別ファイルへの分割。すべての処理はブラウザ内で完結、アップロード不要、完全プライベート。"),
("Split by Ranges", "按范围拆分", "範囲で分割"),
("Extract page ranges into separate files", "将页面范围提取为单独文件", "ページ範囲を個別ファイルに抽出"),
("Extract Pages", "提取页面", "ページ抽出"),
("Pick specific pages into one PDF", "选择特定页面合并为一个PDF", "特定ページを1つのPDFにまとめる"),
("Individual Pages", "逐页拆分", "個別ページ"),
("Split every page into its own file", "将每页拆分为单独文件", "各ページを個別ファイルに分割"),
("Page Ranges", "页面范围", "ページ範囲"),
("Enter ranges separated by commas. Example:", "用逗号分隔范围。示例：", "範囲をカンマで区切って入力。例："),
("creates 3 files", "创建3个文件", "3つのファイルを作成"),
("Select Pages to Extract", "选择要提取的页面", "抽出するページを選択"),
("Click pages to select. Selected pages will be combined into one PDF.", "点击页面选择。选中的页面将合并为一个PDF。", "ページをクリックして選択。選択したページが1つのPDFに結合されます。"),
("Split PDF", "拆分PDF", "PDFを分割"),
("Splitting...", "正在拆分...", "分割中..."),
("Split Complete!", "拆分完成！", "分割完了！"),
("Your PDF has been split.", "您的PDF已拆分。", "PDFが分割されました。"),
("Split Another File", "拆分另一个文件", "別のファイルを分割"),
("How to Split PDF Files Online — Free & Private", "如何在线拆分PDF文件—免费且安全", "PDFファイルをオンライン分割する方法—無料＆安全"),
("Upload PDF", "上传PDF", "PDFをアップロード"),
("Choose Mode", "选择模式", "モードを選択"),
("Select split by ranges, extract specific pages, or split into individual pages.", "选择按范围拆分、提取特定页面或拆分为单个页面。", "範囲指定分割、特定ページ抽出、または個別ページ分割を選択。"),
("Split & Download", "拆分并下载", "分割＆ダウンロード"),
("Click split — processing happens in your browser. Download instantly.", "点击拆分—处理在浏览器中完成。即时下载。", "分割をクリック—処理はブラウザ内で完結。即時ダウンロード。"),
("What is PDF Splitting?", "什么是PDF拆分？", "PDF分割とは？"),
("PDF Split", "PDF拆分", "PDF分割"),
]

# Sort by English string length (longest first) to avoid partial matches
T.sort(key=lambda x: len(x[0]), reverse=True)

# ============================================================
#  Page configurations: (file_path, url_path, html_lang_for_en)
# ============================================================

PAGES = [
    ('index.html', '', 'index.html'),
    ('pdf-to-word/index.html', 'pdf-to-word/', 'pdf-to-word/index.html'),
    ('pdf-merge/index.html', 'pdf-merge/', 'pdf-merge/index.html'),
    ('pricing/index.html', 'pricing/', 'pricing/index.html'),
    ('support/index.html', 'support/', 'support/index.html'),
    ('currency-converter/index.html', 'currency-converter/', 'currency-converter/index.html'),
    ('pdf-split/index.html', 'pdf-split/', 'pdf-split/index.html'),
]

def translate(html, lang):
    """Apply translations to HTML content.
    Uses letter-boundary lookbehind/lookahead for short strings (<=14 chars)
    to prevent partial matches inside other words (e.g. 'or' inside 'Word')."""
    idx = 1 if lang == 'zh' else 2  # 1=zh, 2=ja
    for en, zh, ja in T:
        target = zh if lang == 'zh' else ja
        if en not in html:
            continue
        if len(en) <= 14:
            # Word-boundary safe replacement: only match when not surrounded by letters
            pattern = r'(?<![a-zA-Z])' + re.escape(en) + r'(?![a-zA-Z])'
            html = re.sub(pattern, target, html)
        else:
            html = html.replace(en, target)
    return html

def add_lang_switcher_to_en(html, path):
    """Add language switcher CSS and HTML to English pages."""
    # Add CSS before </style> — check for the CSS rule specifically
    if '.lang-switcher{display:flex' not in html:
        html = html.replace('</style>', LANG_CSS + '\n</style>', 1)

    # Add hreflang tags after canonical
    hreflang = hreflang_tags(path)
    if 'hreflang' not in html:
        html = html.replace('<link rel="canonical"', hreflang + '\n<link rel="canonical">', 1)

    # Add language switcher HTML into header
    # Use a marker that only appears in the HTML div, not in CSS definitions
    switcher = lang_switcher(path, 'en')
    if '<div class="lang-switcher">' not in html:
        html = html.replace('</nav>', switcher + '\n    </nav>', 1)

    return html

def inject_auth_and_nav(html):
    """Inject auth CSS/JS includes and add Pricing/Support nav links."""
    # 1. Add common.css link before </head> (if not already present)
    if '/assets/common.css' not in html:
        css_link = '<link rel="stylesheet" href="/assets/common.css">'
        html = html.replace('</head>', '    ' + css_link + '\n</head>', 1)

    # 2. Add config.js + app.js before </body> (if not already present)
    if '/assets/app.js' not in html:
        js_block = ('<script src="/assets/config.js"></script>\n'
                    '<script src="/assets/app.js"></script>\n'
                    '</body>')
        html = html.replace('</body>', js_block, 1)

    # 3. Add Pricing & Support nav links (if not already present)
    # Insert before the lang-switcher div or before </nav>
    if 'href="/pricing/"' not in html and 'href="/pricing"' not in html:
        nav_links = ('<a href="/pricing/">Pricing</a>\n      '
                     '<a href="/support/">Support</a>')
        if '<div class="lang-switcher">' in html:
            html = html.replace('<div class="lang-switcher">', nav_links + '\n      <div class="lang-switcher">', 1)
        else:
            html = html.replace('</nav>', nav_links + '\n    </nav>', 1)

    # 4. Add Pricing/Support/Currency to footer (if not already present)
    if 'href="/currency-converter/"' not in html:
        # Add to footer-tools if present
        if 'footer-tools' in html:
            html = html.replace(
                '</div>\n    <p>&copy;',
                '<a href="/currency-converter/">Currency Converter</a>\n      <a href="/pricing/">Pricing</a>\n      <a href="/support/">Support</a>\n    </div>\n    <p>&copy;',
                1
            )

    return html

def process_page(file_rel, url_path):
    """Read English HTML, generate zh and ja versions, update English."""
    en_path = os.path.join(BASE, file_rel)
    with open(en_path, 'r', encoding='utf-8') as f:
        en_html = f.read()

    # --- Update English page with switcher + hreflang + auth + nav ---
    en_updated = add_lang_switcher_to_en(en_html, url_path)
    en_updated = inject_auth_and_nav(en_updated)
    with open(en_path, 'w', encoding='utf-8') as f:
        f.write(en_updated)
    print(f'  Updated EN: {file_rel}')

    # --- Generate localized versions ---
    for lang, lang_name in [('zh', 'Chinese'), ('ja', 'Japanese')]:
        localized = translate(en_updated, lang)

        # Update <html lang="en"> to target lang
        localized = localized.replace('<html lang="en">', f'<html lang="{lang}">')

        # Update canonical URL
        old_canonical = f'<link rel="canonical" href="https://toolify.com/{url_path}">'
        new_canonical = f'<link rel="canonical" href="https://toolify.com/{lang}/{url_path}">'
        localized = localized.replace(old_canonical, new_canonical)

        # Protect language switcher from internal link updates
        switcher_placeholder = '__LANG_SWITCHER_PROTECTED__'
        switcher_match = re.search(r'<div class="lang-switcher">.*?</div>', localized)
        saved_switcher = switcher_match.group() if switcher_match else ''
        if saved_switcher:
            localized = localized.replace(saved_switcher, switcher_placeholder)

        # Update internal links to point to localized versions
        # Logo and "All Tools" nav link (href="/")
        localized = localized.replace('href="/" class="logo"', f'href="/{lang}/" class="logo"')
        # Footer tool links and nav links
        for tool_path in ['pdf-to-word/', 'pdf-merge/', 'pdf-split/', 'pricing/', 'support/', 'currency-converter/', '']:
            old_href = f'href="/{tool_path}"' if tool_path else 'href="/"'
            new_href = f'href="/{lang}/{tool_path}"' if tool_path else f'href="/{lang}/"'
            localized = localized.replace(old_href, new_href)

        # Restore language switcher
        if saved_switcher:
            # Update active state: remove active from EN, add to current lang
            restored = saved_switcher.replace('class="lang-link active">EN', 'class="lang-link">EN')
            target_url = f'/{lang}/{url_path}' if url_path else f'/{lang}/'
            restored = restored.replace(
                f'href="{target_url}" class="lang-link">',
                f'href="{target_url}" class="lang-link active">'
            )
            localized = localized.replace(switcher_placeholder, restored)

        # Update og:url if present
        localized = localized.replace(
            f'<meta property="og:url" content="https://toolify.com/{url_path}">',
            f'<meta property="og:url" content="https://toolify.com/{lang}/{url_path}">'
        )

        # Write output
        out_dir = os.path.join(BASE, lang, os.path.dirname(file_rel))
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(BASE, lang, file_rel)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(localized)
        print(f'  Created {lang_name}: {lang}/{file_rel}')

def main():
    print('=== Generating localized pages ===')
    for file_rel, url_path, _ in PAGES:
        print(f'\nProcessing: {file_rel}')
        process_page(file_rel, url_path)

    # Update sitemap
    print('\n=== Updating sitemap.xml ===')
    sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
'''
    for _, path, _ in PAGES:
        p = path.rstrip('/')
        for lang, code in [('en', ''), ('zh', 'zh/'), ('ja', 'ja/')]:
            url = f'https://toolify.com/{code}{p}' if p else f'https://toolify.com/{code}'.rstrip('/')
            if not url.endswith('/') and not p:
                url = url.rstrip('/') + '/' if code else 'https://toolify.com/'
            elif p and code:
                url = f'https://toolify.com/{code}{p}/'
            elif p and not code:
                url = f'https://toolify.com/{p}/'
            elif not p and not code:
                url = 'https://toolify.com/'
            elif not p and code:
                url = f'https://toolify.com/{code}'

            sitemap += f'''  <url>
    <loc>{url}</loc>
    <lastmod>2026-07-08</lastmod>
    <changefreq>{"weekly" if not p else "monthly"}</changefreq>
    <priority>{"1.0" if not p else "0.9"}</priority>
'''
            # Add xhtml:link alternates
            for alt_lang, alt_code in [('en', ''), ('zh', 'zh/'), ('ja', 'ja/')]:
                alt_url = f'https://toolify.com/{alt_code}{p}' if p else f'https://toolify.com/{alt_code}'.rstrip('/')
                if not p and not alt_code:
                    alt_url = 'https://toolify.com/'
                elif not p and alt_code:
                    alt_url = f'https://toolify.com/{alt_code}'
                elif p and alt_code:
                    alt_url = f'https://toolify.com/{alt_code}{p}/'
                else:
                    alt_url = f'https://toolify.com/{p}/'
                sitemap += f'    <xhtml:link rel="alternate" hreflang="{alt_lang}" href="{alt_url}"/>\n'
            sitemap += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{"https://toolify.com/" if not p else f"https://toolify.com/{p}/"}"/>\n'
            sitemap += '  </url>\n'

    sitemap += '</urlset>'

    with open(os.path.join(BASE, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print('  Updated sitemap.xml')

    print('\n=== Done! ===')

if __name__ == '__main__':
    main()
