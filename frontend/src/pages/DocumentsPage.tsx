import { useState } from 'react';
import FileUpload from '../components/FileUpload';
import DocumentPanel from '../components/DocumentPanel';

export default function DocumentsPage() {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-2">Documents</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          Upload and manage your research papers, books, and notes.
        </p>

        <div className="card p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Upload Documents</h2>
          <FileUpload />
        </div>

        <div className="card overflow-hidden" style={{ minHeight: '400px' }}>
          <DocumentPanel
            selectedIds={selectedIds}
            onSelectionChange={setSelectedIds}
          />
        </div>
      </div>
    </div>
  );
}
