/**
 * MINDCARE NER - Progressive Web App (PWA) Offline Manager & Sync Engine
 * Handles IndexedDB local storage when offline and auto-syncs with POST /api/sync
 */

class OfflineSyncManager {
  constructor() {
    this.dbName = 'MindCareOfflineDB';
    this.dbVersion = 1;
    this.db = null;
    this.initDatabase();
    this.registerServiceWorker();
    this.bindNetworkEvents();
  }

  // Register PWA Service Worker
  registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
          .then(reg => console.log('✅ ServiceWorker registered with scope:', reg.scope))
          .catch(err => console.warn('ServiceWorker registration error:', err));
      });
    }
  }

  // Initialize IndexedDB
  initDatabase() {
    const request = indexedDB.open(this.dbName, this.dbVersion);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending_sync')) {
        db.createObjectStore('pending_sync', { keyPath: 'id', autoIncrement: true });
      }
    };

    request.onsuccess = (event) => {
      this.db = event.target.result;
      console.log('✅ MindCare Offline IndexedDB initialized');
      // If currently online, check for pending items to sync
      if (navigator.onLine) {
        this.syncPendingData();
      }
    };

    request.onerror = (event) => {
      console.error('IndexedDB open error:', event.target.error);
    };
  }

  // Queue item for sync
  queueItem(type, data) {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        // LocalStorage fallback
        try {
          const queue = JSON.parse(localStorage.getItem('mindcare_pending_sync') || '[]');
          queue.push({ type, data, timestamp: new Date().toISOString() });
          localStorage.setItem('mindcare_pending_sync', JSON.stringify(queue));
          resolve(true);
        } catch (e) {
          reject(e);
        }
        return;
      }

      const tx = this.db.transaction('pending_sync', 'readwrite');
      const store = tx.objectStore('pending_sync');
      const item = { type, data, timestamp: new Date().toISOString() };
      const req = store.add(item);

      req.onsuccess = () => {
        console.log(`📦 Queued ${type} for offline sync`);
        this.updateSyncBadge();
        resolve(true);
      };
      req.onerror = () => reject(req.error);
    });
  }

  // Synchronize all pending records with the Flask server
  async syncPendingData() {
    if (!navigator.onLine) return;

    let itemsToSync = [];

    if (this.db) {
      itemsToSync = await new Promise((resolve) => {
        const tx = this.db.transaction('pending_sync', 'readonly');
        const store = tx.objectStore('pending_sync');
        const req = store.getAll();
        req.onsuccess = () => resolve(req.result || []);
        req.onerror = () => resolve([]);
      });
    } else {
      itemsToSync = JSON.parse(localStorage.getItem('mindcare_pending_sync') || '[]');
    }

    if (itemsToSync.length === 0) return;

    console.log(`🔄 Syncing ${itemsToSync.length} items with MindCare server...`);
    const statusPill = document.getElementById('offline-banner');
    if (statusPill) {
      statusPill.style.display = 'block';
      statusPill.className = 'alert alert-info text-center m-0 p-2';
      statusPill.innerHTML = `🔄 Synchronizing ${itemsToSync.length} offline activities...`;
    }

    try {
      const response = await fetch('/api/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: itemsToSync })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Sync successful:', result);

        // Clear local queue
        if (this.db) {
          const clearTx = this.db.transaction('pending_sync', 'readwrite');
          clearTx.objectStore('pending_sync').clear();
        }
        localStorage.removeItem('mindcare_pending_sync');

        if (statusPill) {
          statusPill.className = 'alert alert-success text-center m-0 p-2';
          statusPill.innerHTML = `✅ Successfully synchronized ${result.total_synced || itemsToSync.length} activities!`;
          setTimeout(() => { statusPill.style.display = 'none'; }, 3500);
        }
        this.updateSyncBadge();
      }
    } catch (err) {
      console.warn('Sync attempt failed, will retry when connection stabilizes:', err);
    }
  }

  updateSyncBadge() {
    const badge = document.getElementById('pending-sync-badge');
    if (!badge) return;

    if (this.db) {
      const tx = this.db.transaction('pending_sync', 'readonly');
      const store = tx.objectStore('pending_sync');
      const countReq = store.count();
      countReq.onsuccess = () => {
        const count = countReq.result;
        badge.textContent = count > 0 ? `${count} Pending Sync` : '';
        badge.style.display = count > 0 ? 'inline-block' : 'none';
      };
    }
  }

  bindNetworkEvents() {
    const updateOnlineStatus = () => {
      const banner = document.getElementById('offline-banner');
      if (!banner) return;

      if (!navigator.onLine) {
        banner.style.display = 'block';
        banner.className = 'alert alert-warning text-center m-0 p-2';
        banner.innerHTML = '⚠️ <strong>Offline Mode</strong>: Games and cached reminders are fully available. Changes will sync automatically once reconnected.';
      } else {
        banner.style.display = 'none';
        this.syncPendingData();
      }
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    document.addEventListener('DOMContentLoaded', updateOnlineStatus);
  }
}

// Global Offline Sync Manager Instance
window.offlineSyncManager = new OfflineSyncManager();
