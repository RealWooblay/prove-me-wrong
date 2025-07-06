"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Download, Chrome, Twitter, Bot } from "lucide-react"
import Link from "next/link"

export default function HowTo() {
  const downloadExtension = () => {
    // Create a zip file download of the extension
    const link = document.createElement('a');
    link.href = '/extension/manifest.json';
    link.download = 'prove-me-wrong-extension';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-20">
      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Left Column - Extension Guide */}
          <div className="animate-slide-up">
            <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-white to-blue-400 bg-clip-text text-transparent">
              How to Install the Extension
            </h1>

            <div className="space-y-8">
              <Card className="glass-card dark:glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center text-xl">
                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-sm font-bold mr-3">
                      1
                    </div>
                    Download Extension Files
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300 mb-4">
                    Download the Prove Me Wrong browser extension files to get started.
                  </p>
                  <Button
                    onClick={downloadExtension}
                    className="gradient-cta hover:animate-bounce-micro"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download Extension
                  </Button>
                </CardContent>
              </Card>

              <Card className="glass-card dark:glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center text-xl">
                    <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-sm font-bold mr-3">
                      2
                    </div>
                    Install in Chrome
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300 mb-4">
                    Follow these steps to install the extension in Chrome:
                  </p>
                  <div className="space-y-3 text-sm text-gray-300">
                    <div className="flex items-start">
                      <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs mr-3 mt-0.5">1</span>
                      <span>Go to <code className="bg-slate-800 px-2 py-1 rounded">chrome://extensions/</code></span>
                    </div>
                    <div className="flex items-start">
                      <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs mr-3 mt-0.5">2</span>
                      <span>Enable "Developer mode" (toggle in top right)</span>
                    </div>
                    <div className="flex items-start">
                      <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs mr-3 mt-0.5">3</span>
                      <span>Click "Load unpacked" and select the extension folder</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-card dark:glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center text-xl">
                    <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-sm font-bold mr-3">
                      3
                    </div>
                    Start Predicting
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300 mb-4">
                    Once installed, you'll see prediction markets on Twitter. Make predictions and let AI determine the outcomes!
                  </p>
                  <Button
                    onClick={() => window.open("https://twitter.com/RealWooblay", "_blank")}
                    className="gradient-cta hover:animate-bounce-micro"
                  >
                    <Twitter className="mr-2 h-4 w-4" />
                    See Examples
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Right Column - Features */}
          <div className="animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <Card className="glass-card dark:glass-card sticky top-24">
              <CardHeader>
                <CardTitle className="text-2xl">Extension Features</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Bot className="h-5 w-5 text-blue-400" />
                    <div>
                      <div className="font-semibold">AI-Powered Resolution</div>
                      <div className="text-sm text-gray-400">Automatic outcome determination</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Twitter className="h-5 w-5 text-green-400" />
                    <div>
                      <div className="font-semibold">Twitter Integration</div>
                      <div className="text-sm text-gray-400">See markets directly on Twitter</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Chrome className="h-5 w-5 text-purple-400" />
                    <div>
                      <div className="font-semibold">Browser Extension</div>
                      <div className="text-sm text-gray-400">Works on any website</div>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <h3 className="text-lg font-semibold mb-4">How It Works</h3>
                  <div className="space-y-3 text-sm text-gray-300">
                    <div className="flex items-start">
                      <span className="bg-yellow-500 text-black rounded-full w-5 h-5 flex items-center justify-center text-xs mr-3 mt-0.5">1</span>
                      <span>Post a prediction on Twitter</span>
                    </div>
                    <div className="flex items-start">
                      <span className="bg-yellow-500 text-black rounded-full w-5 h-5 flex items-center justify-center text-xs mr-3 mt-0.5">2</span>
                      <span>Others can bet against your prediction</span>
                    </div>
                    <div className="flex items-start">
                      <span className="bg-yellow-500 text-black rounded-full w-5 h-5 flex items-center justify-center text-xs mr-3 mt-0.5">3</span>
                      <span>AI analyzes evidence and determines the outcome</span>
                    </div>
                    <div className="flex items-start">
                      <span className="bg-yellow-500 text-black rounded-full w-5 h-5 flex items-center justify-center text-xs mr-3 mt-0.5">4</span>
                      <span>Winners get paid automatically</span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <h3 className="text-lg font-semibold mb-4">Supported Browsers</h3>
                  <div className="space-y-2">
                    <Badge variant="secondary" className="bg-green-500/20 text-green-400">
                      Chrome
                    </Badge>
                    <Badge variant="secondary" className="bg-blue-500/20 text-blue-400">
                      Edge
                    </Badge>
                    <Badge variant="secondary" className="bg-orange-500/20 text-orange-400">
                      Brave
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
