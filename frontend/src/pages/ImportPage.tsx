import { useState, useRef } from 'react';
import { Upload, FileText, Users, MessageSquare } from 'lucide-react';
import Card from '../components/Card';
import { importApi } from '../api/client';

type SegmentType = 'paragraph' | 'line' | 'turn' | 'qa';

interface SegmentOption {
  value: SegmentType;
  label: string;
  description: string;
  icon: React.ReactNode;
}

const segmentOptions: SegmentOption[] = [
  {
    value: 'paragraph',
    label: '段落分割',
    description: '按空行分割，适合普通文章',
    icon: <FileText className="h-5 w-5" />
  },
  {
    value: 'turn',
    label: '说话人轮次',
    description: '识别"主持人："等标识，按发言分割',
    icon: <Users className="h-5 w-5" />
  },
  {
    value: 'qa',
    label: '问答对',
    description: '将提问和回答组合成片段（推荐用于访谈）',
    icon: <MessageSquare className="h-5 w-5" />
  },
  {
    value: 'line',
    label: '逐行分割',
    description: '每行作为一个片段',
    icon: <FileText className="h-5 w-5" />
  }
];

export default function ImportPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [segmentType, setSegmentType] = useState<SegmentType>('paragraph');
  const [importResult, setImportResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setIsUploading(true);
    setMessage('');
    setImportResult(null);
    
    try {
      const res = await importApi.upload(file, segmentType);
      setImportResult(res.data);
      
      let msg = res.data.message || `成功导入 ${res.data.count} 个文本片段`;
      if (res.data.speakers) {
        const speakerInfo = Object.entries(res.data.speakers)
          .map(([name, count]) => `${name}(${count}次)`)
          .join('，');
        msg += `\n识别到说话人：${speakerInfo}`;
      }
      setMessage(msg);
    } catch (err: any) {
      console.error('Import error:', err);
      const errorMsg = err.response?.data?.detail || '导入失败，请重试';
      setMessage(errorMsg);
    } finally {
      setIsUploading(false);
      // 清空文件输入，允许重复选择同一文件
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-endfield-text-primary mb-2">导入数据</h2>
        <p className="text-endfield-text-secondary">上传文本文件进行分析</p>
      </div>
      
      {/* 分割方式选择 */}
      <Card>
        <h3 className="text-sm font-medium text-endfield-text-secondary mb-3">选择文本分割方式</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {segmentOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setSegmentType(option.value)}
              className={`flex items-start gap-3 p-3 rounded-lg border text-left transition-all ${
                segmentType === option.value
                  ? 'border-endfield-accent bg-endfield-accent/10'
                  : 'border-endfield-border hover:border-endfield-accent/50'
              }`}
            >
              <div className={`mt-0.5 ${
                segmentType === option.value ? 'text-endfield-accent' : 'text-endfield-text-muted'
              }`}>
                {option.icon}
              </div>
              <div>
                <div className={`font-medium ${
                  segmentType === option.value ? 'text-endfield-accent' : 'text-endfield-text-primary'
                }`}>
                  {option.label}
                </div>
                <div className="text-xs text-endfield-text-secondary mt-0.5">
                  {option.description}
                </div>
              </div>
            </button>
          ))}
        </div>
      </Card>
      
      {/* 文件上传区 */}
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
            支持 .txt, .md, .pdf, .doc, .docx 格式文件
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.pdf,.doc,.docx"
            className="hidden"
            onChange={handleFileSelect}
          />
        </div>
        
        {isUploading && (
          <div className="mt-4 text-center text-endfield-text-secondary">
            <div className="inline-block animate-spin mr-2">⟳</div>
            上传并解析中...
          </div>
        )}
        
        {message && (
          <div className={`mt-4 p-3 rounded-lg text-center whitespace-pre-line ${
            message.includes('成功') || message.includes('识别到')
              ? 'bg-green-500/10 text-green-400' 
              : 'bg-red-500/10 text-red-400'
          }`}>
            {message}
          </div>
        )}
        
        {/* 导入结果预览 */}
        {importResult && importResult.segments && importResult.segments.length > 0 && (
          <div className="mt-4 pt-4 border-t border-endfield-border">
            <h4 className="text-sm font-medium text-endfield-text-secondary mb-2">
              片段预览（前3个）
            </h4>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {importResult.segments.slice(0, 3).map((seg: any, idx: number) => (
                <div key={seg.id} className="p-2 bg-endfield-bg-tertiary rounded text-sm">
                  <div className="text-xs text-endfield-text-muted mb-1">
                    片段 {idx + 1} · {seg.content.length} 字符
                  </div>
                  <div className="text-endfield-text-primary line-clamp-2">
                    {seg.content}
                  </div>
                </div>
              ))}
              {importResult.segments.length > 3 && (
                <div className="text-center text-xs text-endfield-text-muted py-1">
                  ...还有 {importResult.segments.length - 3} 个片段
                </div>
              )}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
