// Modern JavaScript for Plivo AI Chatbot Interface

class PlivoChatbotApp {
    constructor() {
        this.currentTab = 'call';
        this.settings = this.loadSettings();
        this.init();
    }

    init() {
        this.setupTabs();
        this.setupForms();
        this.setupPresetPrompts();
        this.setupVoiceSelection();
        this.loadSavedSettings();
    }

    // Tab Management
    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.dataset.tab;
                this.switchTab(tabId);
            });
        });
    }

    switchTab(tabId) {
        // Remove active class from all tabs and contents
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        // Add active class to selected tab and content
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
        document.getElementById(`${tabId}-tab`).classList.add('active');

        this.currentTab = tabId;
    }

    // Form Handling
    setupForms() {
        // Call form
        const callForm = document.getElementById('call-form');
        if (callForm) {
            callForm.addEventListener('submit', (e) => this.handleCallSubmit(e));
        }

        // Settings form
        const settingsForm = document.getElementById('settings-form');
        if (settingsForm) {
            settingsForm.addEventListener('submit', (e) => this.handleSettingsSubmit(e));
        }

        // Auto-save settings on change
        const settingsInputs = document.querySelectorAll('#settings-tab input, #settings-tab select, #settings-tab textarea');
        settingsInputs.forEach(input => {
            input.addEventListener('change', () => this.autoSaveSettings());
        });
    }

    async handleCallSubmit(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const submitButton = e.target.querySelector('button[type="submit"]');
        
        // Show loading state
        this.setButtonLoading(submitButton, true);

        try {
            const response = await fetch('/make-call', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.text();
                this.showCallResult(result);
            } else {
                throw new Error('Call failed');
            }
        } catch (error) {
            this.showAlert('Call failed. Please check your settings and try again.', 'error');
        } finally {
            this.setButtonLoading(submitButton, false);
        }
    }

    async handleSettingsSubmit(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const settings = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });

            if (response.ok) {
                this.settings = settings;
                this.saveSettings();
                this.showAlert('Settings saved successfully!', 'success');
            } else {
                throw new Error('Failed to save settings');
            }
        } catch (error) {
            this.showAlert('Failed to save settings. Please try again.', 'error');
        }
    }

    // Preset Prompts
    setupPresetPrompts() {
        const presetButtons = document.querySelectorAll('.preset-prompt');
        const promptTextarea = document.getElementById('system_prompt');

        presetButtons.forEach(button => {
            button.addEventListener('click', () => {
                const prompt = button.dataset.prompt;
                if (promptTextarea) {
                    promptTextarea.value = prompt;
                    this.autoSaveSettings();
                }
            });
        });
    }

    // Voice Selection
    setupVoiceSelection() {
        const voiceSelect = document.getElementById('voice_id');
        const previewButton = document.getElementById('voice-preview');

        if (previewButton) {
            previewButton.addEventListener('click', () => {
                const selectedVoice = voiceSelect.value;
                this.previewVoice(selectedVoice);
            });
        }
    }

    async previewVoice(voiceId) {
        const previewButton = document.getElementById('voice-preview');
        this.setButtonLoading(previewButton, true);

        try {
            // This would integrate with Cartesia's voice preview API
            // For now, we'll just show a message
            this.showAlert(`Voice preview for ${voiceId} would play here`, 'info');
        } catch (error) {
            this.showAlert('Voice preview failed', 'error');
        } finally {
            this.setButtonLoading(previewButton, false);
        }
    }

    // Settings Management
    loadSettings() {
        const saved = localStorage.getItem('plivo-chatbot-settings');
        return saved ? JSON.parse(saved) : {
            system_prompt: "You are a friendly elementary teacher in India having an audio call. Your output will be converted to audio so don't include special characters in your answers. Respond to what the student said in a short sentence. Be encouraging and educational. Speak clearly and simply.",
            voice_id: "71a7ad14-091c-4e8e-a314-022ece01c121",
            caller_id: "+912269976211",
            target_number: "+919136820958"
        };
    }

    saveSettings() {
        localStorage.setItem('plivo-chatbot-settings', JSON.stringify(this.settings));
    }

    loadSavedSettings() {
        // Load settings into form fields
        Object.keys(this.settings).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.value = this.settings[key];
            }
        });
    }

    autoSaveSettings() {
        const settingsInputs = document.querySelectorAll('#settings-tab input, #settings-tab select, #settings-tab textarea');
        const newSettings = {};

        settingsInputs.forEach(input => {
            if (input.id) {
                newSettings[input.id] = input.value;
            }
        });

        this.settings = { ...this.settings, ...newSettings };
        this.saveSettings();
    }

    // UI Helpers
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner"></span>Processing...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || 'Submit';
        }
    }

    showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;

        // Insert at top of current tab content
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab) {
            activeTab.insertBefore(alert, activeTab.firstChild);
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    showCallResult(htmlResult) {
        // Create a modal or new page to show call result
        const resultWindow = window.open('', '_blank');
        resultWindow.document.write(htmlResult);
    }

    // API Helpers
    async fetchVoices() {
        try {
            const response = await fetch('/api/voices');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Failed to fetch voices:', error);
        }
        return [];
    }

    async fetchCallHistory() {
        try {
            const response = await fetch('/api/call-history');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Failed to fetch call history:', error);
        }
        return [];
    }

    // Initialize call history
    async loadCallHistory() {
        const history = await this.fetchCallHistory();
        const historyContainer = document.getElementById('call-history-list');
        
        if (historyContainer && history.length > 0) {
            historyContainer.innerHTML = history.map(call => `
                <div class="call-entry">
                    <div class="call-info">
                        <strong>${call.target_number}</strong>
                        <div class="call-time">${new Date(call.timestamp).toLocaleString()}</div>
                    </div>
                    <div class="status-indicator status-${call.status}"></div>
                </div>
            `).join('');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.plivoChatbot = new PlivoChatbotApp();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PlivoChatbotApp;
} 