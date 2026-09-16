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
      };
    };
    fetchModels();
  }, []);


  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Cpu className="w-7 h-7 text-blue-600" />
          Model Registry & Versioning
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Active ML fraud classifier and anomaly detection engine versions, performance evaluation metrics, and feature schemas.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 text-sm">Loading model registry...</div>
      ) : error ? (
        <div className="p-8 text-center text-red-600 text-sm">{error}</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {models.map((model, idx) => (
            <Card key={idx} className="p-6 space-y-5 border-t-4 border-t-blue-600">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-bold text-slate-900">{model.model_type}</h3>
                    <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                      {model.status}
                    </span>
                  </div>
                  <p className="text-xs font-mono text-slate-500 mt-1">
                    Name: {model.model_name} • v{model.version} (Schema: {model.feature_schema_version})
                  </p>
                </div>
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                  <ShieldCheck className="w-6 h-6" />
                </div>
              </div>

              {/* Evaluation Metrics Grid */}
              <div>
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1">
                  <BarChart2 className="w-4 h-4 text-blue-600" /> Measured Performance Metrics
                </h4>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(model.metrics).map(([key, val]) => (
                    <div key={key} className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="text-[10px] font-medium text-slate-500 uppercase tracking-tight">
                        {key.replace('_', ' ')}
                      </div>
                      <div className="text-base font-bold text-slate-900 mt-0.5">
                        {typeof val === 'number' ? (val < 1 ? (val * 100).toFixed(1) + '%' : val) : String(val)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Metadata & Features */}
              {model.metadata?.features && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <Activity className="w-4 h-4 text-blue-600" /> Active Feature Architecture ({model.metadata.features.length})
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {model.metadata.features.map((feat: string, fIdx: number) => (
                      <span key={fIdx} className="text-xs font-mono bg-slate-100 text-slate-700 border border-slate-200 px-2 py-0.5 rounded">
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
