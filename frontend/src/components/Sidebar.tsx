import {
  Bot,
  Database,
  FileText,
  HardDrive,
  UploadCloud,
} from "lucide-react";

function Sidebar() {
  return (
    <aside className="sidebar">
      <section className="sidebar-section">
        <div className="section-heading">
          <div>
            <span className="section-label">Workspace</span>
            <h2>Knowledge Base</h2>
          </div>

          <span className="document-count">0</span>
        </div>

        <button className="upload-card" type="button">
          <span className="upload-icon-wrapper">
            <UploadCloud size={24} />
          </span>

          <strong>Upload documents</strong>
          <span>PDF or TXT files</span>
        </button>
      </section>

      <section className="sidebar-section documents-section">
        <div className="list-heading">
          <FileText size={15} />
          <span>Documents</span>
        </div>

        <div className="empty-documents">
          <div className="empty-document-icon">
            <HardDrive size={20} />
          </div>

          <p>No documents yet</p>
          <span>Upload a file to begin building your local knowledge base.</span>
        </div>
      </section>

      <section className="system-card">
        <div className="system-card-heading">
          <span>Local services</span>
          <span className="online-label">Online</span>
        </div>

        <div className="service-row">
          <div className="service-name">
            <Bot size={16} />
            <span>Foundry Local</span>
          </div>

          <span className="service-status-dot" />
        </div>

        <div className="service-row">
          <div className="service-name">
            <Database size={16} />
            <span>Vector Database</span>
          </div>

          <span className="service-status-dot" />
        </div>
      </section>
    </aside>
  );
}

export default Sidebar;