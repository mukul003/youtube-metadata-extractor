/**
 * YouTube Metadata Studio - Frontend Application Logic
 */

let currentMetadata = null;
let selectedThumbnailUrl = '';
let selectedThumbnailLabel = 'Max HD';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    if (window.lucide) {
        lucide.createIcons();
    }

    setupTheme();
    setupInputControls();
    setupFormSubmission();
    setupCopyAndDownloads();
});

/* ==========================================================================
   Theme Setup (Dark / Light)
   ========================================================================== */
function setupTheme() {
    const themeBtn = document.getElementById('themeToggleBtn');
    const sunIcon = document.getElementById('themeSun');
    const moonIcon = document.getElementById('themeMoon');
    const html = document.documentElement;

    const savedTheme = localStorage.getItem('yt_studio_theme') || 'dark';
    if (savedTheme === 'light') {
        html.classList.remove('dark');
        sunIcon.classList.remove('hidden');
        moonIcon.classList.add('hidden');
    } else {
        html.classList.add('dark');
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
    }

    themeBtn.addEventListener('click', () => {
        const isDark = html.classList.toggle('dark');
        localStorage.setItem('yt_studio_theme', isDark ? 'dark' : 'light');
        sunIcon.classList.toggle('hidden', isDark);
        moonIcon.classList.toggle('hidden', !isDark);
    });
}

/* ==========================================================================
   Input Field Controls (Paste, Clear, Sample Clicks)
   ========================================================================== */
function setupInputControls() {
    const urlInput = document.getElementById('urlInput');
    const pasteBtn = document.getElementById('pasteBtn');
    const clearBtn = document.getElementById('clearInputBtn');

    urlInput.addEventListener('input', () => {
        if (urlInput.value.trim().length > 0) {
            clearBtn.classList.remove('hidden');
        } else {
            clearBtn.classList.add('hidden');
        }
    });

    clearBtn.addEventListener('click', () => {
        urlInput.value = '';
        clearBtn.classList.add('hidden');
        urlInput.focus();
    });

    pasteBtn.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                urlInput.value = text.trim();
                clearBtn.classList.remove('hidden');
                showToast('Pasted link from clipboard', 'info');
            }
        } catch (err) {
            showToast('Unable to read clipboard. Please paste manually.', 'error');
        }
    });

    // Sample video link buttons
    document.querySelectorAll('.sample-link').forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleUrl = btn.getAttribute('data-url');
            urlInput.value = sampleUrl;
            clearBtn.classList.remove('hidden');
            document.getElementById('extractForm').dispatchEvent(new Event('submit'));
        });
    });
}

/* ==========================================================================
   Metadata Fetching & Form Submission
   ========================================================================== */
function setupFormSubmission() {
    const form = document.getElementById('extractForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnIcon = document.getElementById('btnSearchIcon');
    const loadingState = document.getElementById('loadingState');
    const errorBanner = document.getElementById('errorBanner');
    const errorMessage = document.getElementById('errorMessage');
    const resultsSection = document.getElementById('resultsSection');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = document.getElementById('urlInput').value.trim();
        if (!url) return;

        // UI Loading state
        submitBtn.disabled = true;
        btnText.textContent = 'Extracting...';
        btnIcon.setAttribute('data-lucide', 'loader-2');
        btnIcon.classList.add('animate-spin');
        if (window.lucide) lucide.createIcons();

        loadingState.classList.remove('hidden');
        errorBanner.classList.add('hidden');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('/api/metadata', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Failed to extract video metadata');
            }

            currentMetadata = data.data;
            renderMetadata(currentMetadata);

            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            showToast('Metadata loaded successfully!', 'success');

        } catch (err) {
            errorMessage.textContent = err.message || 'An error occurred while fetching video data.';
            errorBanner.classList.remove('hidden');
            errorBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = 'Fetch Metadata';
            btnIcon.setAttribute('data-lucide', 'search');
            btnIcon.classList.remove('animate-spin');
            loadingState.classList.add('hidden');
            if (window.lucide) lucide.createIcons();
        }
    });
}

/* ==========================================================================
   Render Metadata to UI
   ========================================================================== */
function renderMetadata(data) {
    // 1. HD Thumbnail Preview & Variants
    selectedThumbnailUrl = data.hd_thumbnail;
    selectedThumbnailLabel = 'Max HD';
    const previewImg = document.getElementById('thumbnailPreview');
    previewImg.src = data.hd_thumbnail;

    const thumbOpenBtn = document.getElementById('thumbOpenBtn');
    thumbOpenBtn.href = data.hd_thumbnail;

    const variantsContainer = document.getElementById('thumbVariantsContainer');
    variantsContainer.innerHTML = '';

    if (data.thumbnail_variants && data.thumbnail_variants.length > 0) {
        data.thumbnail_variants.forEach((v, index) => {
            const pill = document.createElement('button');
            pill.type = 'button';
            const isActive = index === 0;
            pill.className = `px-2.5 py-1 rounded-lg text-xs font-medium border transition ${
                isActive 
                    ? 'bg-red-600 text-white border-red-500 shadow-sm' 
                    : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`;
            pill.textContent = `${v.badge || v.label}`;

            pill.addEventListener('click', () => {
                selectedThumbnailUrl = v.url;
                selectedThumbnailLabel = v.badge || v.label;
                previewImg.src = v.url;
                thumbOpenBtn.href = v.url;
                document.getElementById('thumbQualityBadge').textContent = selectedThumbnailLabel;

                // Update active styles
                variantsContainer.querySelectorAll('button').forEach(b => {
                    b.className = 'px-2.5 py-1 rounded-lg text-xs font-medium border transition bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700';
                });
                pill.className = 'px-2.5 py-1 rounded-lg text-xs font-medium border transition bg-red-600 text-white border-red-500 shadow-sm';
            });

            variantsContainer.appendChild(pill);
        });
    }

    // 2. Channel & Video Info
    document.getElementById('channelName').textContent = data.channel || 'Unknown Channel';
    const channelLink = document.getElementById('channelLink');
    if (data.channel_url) {
        channelLink.href = data.channel_url;
        channelLink.classList.remove('hidden');
    } else {
        channelLink.classList.add('hidden');
    }

    const channelInitials = (data.channel || 'YT').substring(0, 2).toUpperCase();
    document.getElementById('channelAvatar').textContent = channelInitials;

    // Category
    document.getElementById('categoryVal').textContent = data.category || 'General';

    // Date Published
    document.getElementById('dateVal').textContent = data.date_published || data.date_iso || 'N/A';

    // Duration & Views
    document.getElementById('durationVal').textContent = data.duration_formatted || 'N/A';
    document.getElementById('viewsVal').textContent = data.view_count_formatted || '0';

    // Video ID
    document.getElementById('videoIdVal').textContent = data.id;

    // 3. Title Card
    document.getElementById('titleText').textContent = data.title;
    document.getElementById('titleCharCount').textContent = `${data.title.length} chars`;

    // 4. Tags Card
    const tagsContainer = document.getElementById('tagsContainer');
    tagsContainer.innerHTML = '';
    const tagsCountBadge = document.getElementById('tagsCountBadge');

    if (data.tags && data.tags.length > 0) {
        tagsCountBadge.textContent = `${data.tags.length} tags`;
        data.tags.forEach(tag => {
            const tagChip = document.createElement('button');
            tagChip.type = 'button';
            tagChip.className = 'px-3 py-1.5 rounded-lg bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 flex items-center gap-1.5 transition active:scale-95 group hover:border-red-500/50';
            tagChip.innerHTML = `
                <span>${escapeHtml(tag)}</span>
                <i data-lucide="copy" class="w-3 h-3 text-slate-400 group-hover:text-white transition"></i>
            `;
            tagChip.title = `Click to copy: "${tag}"`;

            tagChip.addEventListener('click', () => {
                copyToClipboard(tag, `Copied tag: "${tag}"`, tagChip);
            });

            tagsContainer.appendChild(tagChip);
        });
    } else {
        tagsCountBadge.textContent = '0 tags';
        tagsContainer.innerHTML = '<span class="text-xs text-slate-500 italic p-2">This video has no public tags.</span>';
    }

    // 5. Description Card
    const descContainer = document.getElementById('descContainer');
    const descText = data.description || 'No description provided.';
    descContainer.textContent = descText;

    const wordCount = descText.trim() ? descText.trim().split(/\s+/).length : 0;
    document.getElementById('descStats').textContent = `${wordCount} words • ${descText.length} chars`;

    // Re-create icons for freshly inserted elements
    if (window.lucide) {
        lucide.createIcons();
    }
}

/* ==========================================================================
   Copy & Download Handlers
   ========================================================================== */
function setupCopyAndDownloads() {
    // 1. Copy Title
    document.getElementById('copyTitleBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        copyToClipboard(currentMetadata.title, 'Title copied to clipboard!', this);
    });

    // 2. Copy Description
    document.getElementById('copyDescBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        copyToClipboard(currentMetadata.description, 'Description copied to clipboard!', this);
    });

    // 3. Copy Tags (Comma-Separated)
    document.getElementById('copyTagsCommaBtn').addEventListener('click', function() {
        if (!currentMetadata || !currentMetadata.tags || currentMetadata.tags.length === 0) {
            showToast('No tags to copy', 'error');
            return;
        }
        copyToClipboard(currentMetadata.tags_comma, 'All tags copied (comma-separated)!', this);
    });

    // 4. Copy Tags (Hashtags)
    document.getElementById('copyTagsHashtagsBtn').addEventListener('click', function() {
        if (!currentMetadata || !currentMetadata.tags || currentMetadata.tags.length === 0) {
            showToast('No tags to copy', 'error');
            return;
        }
        copyToClipboard(currentMetadata.tags_hashtag, 'Tags copied as #hashtags!', this);
    });

    // 5. Copy Category
    document.getElementById('copyCategoryBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        copyToClipboard(currentMetadata.category, `Category copied: ${currentMetadata.category}`, this);
    });

    // 6. Copy Date Published
    document.getElementById('copyDateBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        copyToClipboard(currentMetadata.date_published, `Date copied: ${currentMetadata.date_published}`, this);
    });

    // 7. Copy Channel
    document.getElementById('copyChannelBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        copyToClipboard(currentMetadata.channel, `Channel copied: ${currentMetadata.channel}`, this);
    });

    // 8. Copy Video URL
    document.getElementById('copyVideoLinkBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        copyToClipboard(currentMetadata.url, 'Video link copied to clipboard!', this);
    });

    // 9. Copy Thumbnail URL
    document.getElementById('copyThumbUrlBtn').addEventListener('click', function() {
        if (!selectedThumbnailUrl) return;
        copyToClipboard(selectedThumbnailUrl, 'HD Thumbnail link copied!', this);
    });

    // 10. Copy All Details (Full Summary)
    document.getElementById('copyAllSummaryBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        copyToClipboard(currentMetadata.summary_text, 'Full video summary copied!', this);
    });

    // ================= DOWNLOAD HANDLERS =================

    // Download HD Thumbnail Image
    document.getElementById('downloadThumbBtn').addEventListener('click', function() {
        if (!currentMetadata || !selectedThumbnailUrl) return;
        const encodedUrl = encodeURIComponent(selectedThumbnailUrl);
        const encodedTitle = encodeURIComponent(currentMetadata.title);
        const downloadUrl = `/api/download-thumbnail?url=${encodedUrl}&title=${encodedTitle}&res=${encodeURIComponent(selectedThumbnailLabel)}`;
        
        triggerDirectDownload(downloadUrl);
        showToast('Starting HD Thumbnail download...', 'info');
    });

    // Download All Metadata as JSON
    document.getElementById('downloadJsonBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        const jsonStr = JSON.stringify(currentMetadata, null, 2);
        downloadFileViaBlob(jsonStr, `${sanitizeFilename(currentMetadata.title)}_metadata.json`, 'application/json');
        showToast('Downloaded metadata as JSON', 'success');
    });

    // Download All Metadata as Text
    document.getElementById('downloadTextBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        downloadFileViaBlob(currentMetadata.summary_text, `${sanitizeFilename(currentMetadata.title)}_summary.txt`, 'text/plain');
        showToast('Downloaded metadata as Text', 'success');
    });

    // Download All Metadata as Markdown
    document.getElementById('downloadMdBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        downloadFileViaBlob(currentMetadata.summary_markdown, `${sanitizeFilename(currentMetadata.title)}_summary.md`, 'text/markdown');
        showToast('Downloaded metadata as Markdown', 'success');
    });

    // Download Tags (.txt)
    document.getElementById('downloadTagsBtn').addEventListener('click', function() {
        if (!currentMetadata || !currentMetadata.tags || currentMetadata.tags.length === 0) {
            showToast('No tags to download', 'error');
            return;
        }
        const text = currentMetadata.tags_lines || currentMetadata.tags_comma;
        downloadFileViaBlob(text, `${sanitizeFilename(currentMetadata.title)}_tags.txt`, 'text/plain');
        showToast('Downloaded tags as .txt', 'success');
    });

    // Download Description (.txt)
    document.getElementById('downloadDescBtn').addEventListener('click', function() {
        if (!currentMetadata) return;
        downloadFileViaBlob(currentMetadata.description, `${sanitizeFilename(currentMetadata.title)}_description.txt`, 'text/plain');
        showToast('Downloaded description as .txt', 'success');
    });
}

/* ==========================================================================
   Helper Functions (Clipboard, Download, Toast, Sanitization)
   ========================================================================== */

function copyToClipboard(text, successMsg = 'Copied to clipboard!', btn = null) {
    if (!text) return;

    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            handleCopySuccess(successMsg, btn);
        }).catch(() => {
            fallbackCopyText(text, successMsg, btn);
        });
    } else {
        fallbackCopyText(text, successMsg, btn);
    }
}

function fallbackCopyText(text, successMsg, btn) {
    try {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.left = '-999999px';
        textarea.style.top = '-999999px';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        handleCopySuccess(successMsg, btn);
    } catch (e) {
        showToast('Failed to copy text', 'error');
    }
}

function handleCopySuccess(successMsg, btn) {
    showToast(successMsg, 'success');
    if (btn) {
        const originalContent = btn.innerHTML;
        btn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-green-400"></i><span class="text-green-400 font-bold">Copied!</span>`;
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {
            btn.innerHTML = originalContent;
            if (window.lucide) lucide.createIcons();
        }, 1800);
    }
}

function downloadFileViaBlob(content, filename, mimeType = 'text/plain') {
    const blob = new Blob([content], { type: `${mimeType};charset=utf-8;` });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function triggerDirectDownload(url) {
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = url;
    document.body.appendChild(iframe);
    setTimeout(() => {
        document.body.removeChild(iframe);
    }, 10000);
}

function sanitizeFilename(name) {
    if (!name) return 'youtube';
    return name.replace(/[\\/*?:"<>|]/g, '').trim().replace(/\s+/g, '_').substring(0, 50);
}

function escapeHtml(string) {
    if (!string) return '';
    return String(string)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl text-xs sm:text-sm font-semibold border backdrop-blur transition';

    let iconName = 'info';
    let colorClasses = 'bg-slate-900/95 text-white border-slate-700';

    if (type === 'success') {
        iconName = 'check-circle';
        colorClasses = 'bg-emerald-950/95 text-emerald-200 border-emerald-700/80';
    } else if (type === 'error') {
        iconName = 'alert-triangle';
        colorClasses = 'bg-rose-950/95 text-rose-200 border-rose-700/80';
    }

    toast.className += ` ${colorClasses}`;
    toast.innerHTML = `
        <i data-lucide="${iconName}" class="w-4 h-4 shrink-0"></i>
        <span>${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();

    setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => {
            if (toast.parentElement) toast.parentElement.removeChild(toast);
        }, 300);
    }, 2800);
}
