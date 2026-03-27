import { useState, useRef } from 'react';
import { Upload } from 'lucide-react';
import Card from '../components/Card';
import { importApi } from '../api/client';

export default function ImportPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setIsUploading(true);
    setMessage('');
    
    try {
      const res = await importApi.upload(file);
      setMessage(`成功导入 ${res.data.count} 个文本片段`);
    } catch (err) {
      setMessage('导入失败，请重试');
    } finally {
      setIsUploading(false);
    }
  };
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-endfield-text-primary mb-2">导入数据</h2>
        <p className="text-endfield-text-secondary">上传文本文件进行分析</p>
      </div>
      
      <Card>
        <div 
          className="border-2 border-dashed border-endfield-border rounded-lg p-12 text-center hover:border-endfield-accent/50 transition-colors cursor-pointer"
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="mx-auto h-12 w-12 text-endfield-text-muted mb-4" />
          <p className="text-lg font-medium text-endfield-text-primary mb-2">
            点击或拖拽上传文件
          </p>
          <p className="text-sm text-endfield-text-muted">
            支持 .txt, .md 格式文件
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md"
            className="hidden"
            onChange={handleFileSelect}
          />
        </div>
        
        {isUploading && (
          <div className="mt-4 text-center text-endfield-text-secondary">
            上传中...
          </div>
        )}
        
        {message && (
          <div className={`mt-4 p-3 rounded-lg text-center ${
            message.includes('成功') ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
          }`}>
            {message}
          </div>
        )}
      </Card>
    </div>
  );
}
