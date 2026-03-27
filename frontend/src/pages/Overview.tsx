import { useEffect } from 'react';
import { Code, FolderTree, FileText, Activity } from 'lucide-react';
import Card from '../components/Card';
import { useStore } from '../store';
import { codesApi, categoriesApi, importApi } from '../api/client';

export default function Overview() {
  const { codes, categories, segments, setCodes, setCategories, setSegments } = useStore();
  
  useEffect(() => {
    codesApi.list().then(res => setCodes(res.data));
    categoriesApi.list().then(res => setCategories(res.data));
    importApi.listSegments().then(res => setSegments(res.data));
  }, []);
  
  const stats = [
    { label: '代码数量', value: codes.length, icon: Code, color: 'text-blue-400' },
    { label: '类属数量', value: categories.length, icon: FolderTree, color: 'text-purple-400' },
    { label: '文本片段', value: segments.length, icon: FileText, color: 'text-green-400' },
    { label: '系统状态', value: '正常', icon: Activity, color: 'text-endfield-accent' },
  ];
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-endfield-text-primary mb-2">概览</h2>
        <p className="text-endfield-text-secondary">项目整体状态监控</p>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="flex items-center gap-4">
            <div className={`p-3 rounded-lg bg-endfield-bg-secondary ${stat.color}`}>
              <stat.icon size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-endfield-text-primary">{stat.value}</p>
              <p className="text-sm text-endfield-text-muted">{stat.label}</p>
            </div>
          </Card>
        ))}
      </div>
      
      {/* Recent Codes */}
      <Card title="最近代码">
        {codes.length === 0 ? (
          <div className="text-center py-8 text-endfield-text-muted">
            <p>暂无代码，请先导入数据并进行编码</p>
          </div>
        ) : (
          <div className="space-y-2">
            {codes.slice(0, 5).map((code) => (
              <div 
                key={code.id} 
                className="flex items-center justify-between p-3 bg-endfield-bg-secondary rounded-lg"
              >
                <div>
                  <span className="font-medium text-endfield-text-primary">{code.label}</span>
                  <span className="ef-badge-accent ml-2">{code.level}</span>
                </div>
                <span className="text-sm text-endfield-text-muted">{code.created_by}</span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
