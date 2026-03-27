import { useEffect, useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import { useStore } from '../store';
import { codesApi } from '../api/client';

export default function CodesPage() {
  const { codes, setCodes, removeCode } = useStore();
  const [isCreating, setIsCreating] = useState(false);
  const [newCode, setNewCode] = useState({ label: '', definition: '', level: 'open' as const });
  
  useEffect(() => {
    codesApi.list().then(res => setCodes(res.data));
  }, []);
  
  const handleCreate = async () => {
    if (!newCode.label) return;
    const res = await codesApi.create(newCode);
    setCodes([res.data, ...codes]);
    setIsCreating(false);
    setNewCode({ label: '', definition: '', level: 'open' });
  };
  
  const handleDelete = async (id: string) => {
    await codesApi.delete(id);
    removeCode(id);
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-endfield-text-primary mb-2">代码本</h2>
          <p className="text-endfield-text-secondary">管理质性编码</p>
        </div>
        <Button onClick={() => setIsCreating(true)}>
          <Plus size={18} className="mr-1" />
          新建代码
        </Button>
      </div>
      
      {/* Create Form */}
      {isCreating && (
        <Card accent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-endfield-text-secondary mb-1">
                代码标签
              </label>
              <input
                type="text"
                className="ef-input"
                value={newCode.label}
                onChange={(e) => setNewCode({ ...newCode, label: e.target.value })}
                placeholder="输入代码标签"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-endfield-text-secondary mb-1">
                定义
              </label>
              <textarea
                className="ef-input h-24 resize-none"
                value={newCode.definition}
                onChange={(e) => setNewCode({ ...newCode, definition: e.target.value })}
                placeholder="输入代码定义"
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreate}>保存</Button>
              <Button variant="secondary" onClick={() => setIsCreating(false)}>取消</Button>
            </div>
          </div>
        </Card>
      )}
      
      {/* Codes List */}
      <div className="space-y-3">
        {codes.map((code) => (
          <Card key={code.id} className="group">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-endfield-text-primary">
                    {code.label}
                  </h3>
                  <span className="ef-badge-accent">{code.level}</span>
                  <span className="text-xs text-endfield-text-muted font-mono">#{code.id}</span>
                </div>
                <p className="text-endfield-text-secondary">{code.definition || '暂无定义'}</p>
                <div className="mt-3 flex items-center gap-4 text-sm text-endfield-text-muted">
                  <span>创建者: {code.created_by}</span>
                  <span>版本: {code.version}</span>
                </div>
              </div>
              <button 
                className="p-2 text-endfield-text-muted hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                onClick={() => handleDelete(code.id)}
              >
                <Trash2 size={18} />
              </button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
