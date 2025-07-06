import { NextResponse } from 'next/server';

export async function GET() {
    // Create a simple HTML page with download instructions
    const html = `
<!DOCTYPE html>
<html>
<head>
    <title>Download Prove Me Wrong Extension</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 600px; 
            margin: 50px auto; 
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .container { background: #2a2a2a; padding: 30px; border-radius: 10px; }
        .step { margin: 20px 0; padding: 15px; background: #333; border-radius: 5px; }
        .code { background: #000; padding: 10px; border-radius: 5px; font-family: monospace; }
        .download-btn { 
            background: #007bff; 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px;
            margin: 10px 5px;
        }
        .download-btn:hover { background: #0056b3; }
        .download-btn.zip { background: #28a745; }
        .download-btn.zip:hover { background: #1e7e34; }
        .warning { background: #ffc107; color: #000; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .file-list { background: #000; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .file-item { margin: 5px 0; color: #0f0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Download Prove Me Wrong Extension</h1>
        
        <div class="step">
            <h3>Step 1: Download Extension Files</h3>
            <p>Click the button below to download all extension files:</p>
            <button class="download-btn" onclick="downloadAll()">📁 Download All Files</button>
            <div class="warning">
                <strong>Note:</strong> All files will download automatically. Create a folder and extract them there.
            </div>
            <div class="file-list">
                <strong>Files that will be downloaded:</strong>
                <div class="file-item">• manifest.json</div>
                <div class="file-item">• background.js</div>
                <div class="file-item">• content-script.js</div>
                <div class="file-item">• inpage-proxy.js</div>
                <div class="file-item">• overlay.css</div>
                <div class="file-item">• icons/icon128.png</div>
                <div class="file-item">• icons/icon48.png</div>
            </div>
        </div>
        
        <div class="step">
            <h3>Step 2: Install in Chrome</h3>
            <ol>
                <li>Go to <span class="code">chrome://extensions/</span></li>
                <li>Enable "Developer mode" (toggle in top right)</li>
                <li>Click "Load unpacked" and select the folder with all the downloaded files</li>
            </ol>
        </div>
        
        <div class="step">
            <h3>Step 3: Start Predicting!</h3>
            <p>Once installed, you'll see prediction markets on Twitter. Make predictions and let AI determine the outcomes!</p>
        </div>
    </div>

    <script>
        function downloadAll() {
            const files = [
                '/extension/manifest.json',
                '/extension/background.js',
                '/extension/content-script.js',
                '/extension/inpage-proxy.js',
                '/extension/overlay.css',
                '/extension/icons/icon128.png',
                '/extension/icons/icon48.png'
            ];
            
            files.forEach((file, index) => {
                setTimeout(() => {
                    const link = document.createElement('a');
                    link.href = file;
                    link.download = file.split('/').pop();
                    link.target = '_blank';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }, index * 300); // Stagger downloads
            });
            
            setTimeout(() => {
                alert('All extension files downloaded! Create a folder, put all files in it, and follow the installation steps.');
            }, files.length * 300 + 1000);
        }
    </script>
</body>
</html>`;

    return new NextResponse(html, {
        headers: {
            'Content-Type': 'text/html',
        },
    });
} 