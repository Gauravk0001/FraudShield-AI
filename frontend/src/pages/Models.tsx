import React, { useState, useEffect } from 'react';
import { Cpu, ShieldCheck, Activity, BarChart2 } from 'lucide-react';
import { apiRequest } from '../services/api';
import { Card } from '../components/ui/Card';

interface ModelVersion {
  model_name: string;
  version: string;
  model_type: string;
  feature_schema_version: string;
  metrics: Record<string, any>;
  status: string;
  metadata: Record<string, any>;
}

export const ModelsPage: React.FC = () => {
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const data = await apiRequest<ModelVersion[]>('/models');
        setModels(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load model registry');
      } finally {
        setLoading(false);
      }
    };
    fetchModels();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <Cpu className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          Model Registry & Versioning
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Active ML fraud classifier and anomaly detection engine versions, performance evaluation metrics, and feature schemas.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 dark:text-slate-400 text-xs">Loading model registry...</div>
      ) : error ? (
        <div className="p-8 text-center text-red-600 dark:text-red-400 text-xs">{error}</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {models.map((model, idx) => (
            <Card key={idx} className="space-y-5 border-t-4 border-t-blue-600">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">{model.model_type}</h3>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                      {model.status}
                    </span>
                  </div>
                  <p className="text-xs font-mono text-slate-500 dark:text-slate-400 mt-1">
                    Name: {model.model_name} • v{model.version} (Schema: {model.feature_schema_version})
                  </p>
                </div>
                <div className="w-9 h-9 rounded-lg bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5" />
                </div>
              </div>

              {/* Evaluation Metrics Grid */}
              <div>
                <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1">
                  <BarChart2 className="w-4 h-4 text-blue-600 dark:text-blue-400" /> Measured Performance Metrics
                </h4>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(model.metrics).map(([key, val]) => (
                    <div key={key} className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-btn border border-slate-200 dark:border-slate-800">
                      <div className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-tight">
                        {key.replace('_', ' ')}
                      </div>
                      <div className="text-sm font-bold text-slate-900 dark:text-slate-100 mt-0.5">
                        {typeof val === 'number' ? (val < 1 ? (val * 100).toFixed(1) + '%' : val) : String(val)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Metadata & Features */}
              {model.metadata?.features && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <Activity className="w-4 h-4 text-blue-600 dark:text-blue-400" /> Active Feature Architecture ({model.metadata.features.length})
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {model.metadata.features.map((feat: string, fIdx: number) => (
                      <span key={fIdx} className="text-[11px] font-mono bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 px-2 py-0.5 rounded">
                        {feat}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default ModelsPage;
