document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    const resultsTemplate = document.getElementById('resultsTemplate');
    const trendsContainer = document.getElementById('trendsContainer');
    const trendTemplate = document.getElementById('trendTemplate');

    let currentFile = null;

    // Fetch trends on load
    fetchTrends();

    // --- Drag and Drop Logic --- //

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drop-zone--over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drop-zone--over');
        }, false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    dropZone.addEventListener('click', () => {
        if (!currentFile) fileInput.click();
    });

    fileInput.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            handleFiles(this.files);
        }
    });

    removeImageBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // prevent clicking dropzone
        currentFile = null;
        fileInput.value = '';
        previewContainer.style.display = 'none';
        submitBtn.disabled = true;
    });

    // --- Form Submission Logic --- //

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!currentFile) return;

        const formData = new FormData(form);
        formData.set('image', currentFile); // ensure our dropped file is used

        // UI Reset & Loading State
        submitBtn.disabled = true;
        resultsSection.style.display = 'none';
        loadingIndicator.style.display = 'block';
        resultsSection.innerHTML = ''; // clear old results

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                renderResults(data);
            } else {
                alert('Error analyzing image: ' + (data.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('A network error occurred while reaching the server.');
        } finally {
            loadingIndicator.style.display = 'none';
            submitBtn.disabled = false;
        }
    });

    // --- Helper Functions --- //

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        const file = files[0];

        if (!file.type.match('image.*')) {
            alert('Please upload an image file (JPG, PNG, WEBP).');
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            alert('File is too large. Max size is 10MB.');
            return;
        }

        currentFile = file;

        // Preview image
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function () {
            imagePreview.src = reader.result;
            previewContainer.style.display = 'flex';
            submitBtn.disabled = false;
        }
    }

    function renderResults(data) {
        // Clone template
        const clone = resultsTemplate.content.cloneNode(true);

        // 1. Skin Tone Parsing
        const skinTone = data.skin_tone;
        clone.querySelector('#skinToneName').textContent = skinTone.category || "Unknown";

        if (skinTone.rgb) {
            const [r, g, b] = skinTone.rgb;
            clone.querySelector('#skinToneSwatch').style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
        } else {
            clone.querySelector('#skinToneSwatch').style.backgroundColor = '#ccc'; // fallback
        }

        // 2. AI Recommendations Parsing
        const recs = data.recommendations;

        if (!recs || typeof recs !== 'object') {
            clone.querySelector('#styleSummary').textContent = "Model failed to return structured data. Raw output: " + JSON.stringify(recs);
            resultsSection.appendChild(clone);
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        clone.querySelector('#styleSummary').textContent = recs.summary || "Here is your personalized style guide.";

        // Colors
        const colorPalette = clone.querySelector('#colorPalette');
        if (recs.colors && Array.isArray(recs.colors)) {
            recs.colors.forEach(color => {
                const div = document.createElement('div');
                div.className = 'palette-color';
                div.style.backgroundColor = color;
                div.title = color;
                colorPalette.appendChild(div);
            });
        }

        // Outfits
        const outfitList = clone.querySelector('#outfitList');
        if (recs.outfit_recommendations && Array.isArray(recs.outfit_recommendations)) {
            recs.outfit_recommendations.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                outfitList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = "No outfit recommendations available.";
            outfitList.appendChild(li);
        }

        // Accessories
        const accessoryList = clone.querySelector('#accessoryList');
        if (recs.accessories && Array.isArray(recs.accessories)) {
            recs.accessories.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                accessoryList.appendChild(li);
            });
        }

        // Hairstyles
        const hairstyleList = clone.querySelector('#hairstyleList');
        if (recs.hairstyles && Array.isArray(recs.hairstyles)) {
            recs.hairstyles.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                hairstyleList.appendChild(li);
            });
        }

        // Shopping Links
        const shoppingList = clone.querySelector('#shoppingList');
        if (recs.shopping_links && Array.isArray(recs.shopping_links)) {
            recs.shopping_links.forEach(link => {
                const card = document.createElement('div');
                card.className = 'shopping-card';
                card.innerHTML = `
                    <span class="store-badge"><i class="fa-solid fa-store"></i> ${link.store || 'Store'}</span>
                    <h3>${link.item || 'Fashion Item'}</h3>
                    <a href="${link.url || '#'}" target="_blank" rel="noopener noreferrer" class="buy-btn">
                        Shop Now <i class="fa-solid fa-arrow-right"></i>
                    </a>
                `;
                shoppingList.appendChild(card);
            });
        } else {
            shoppingList.innerHTML = "<p>No specific shopping links generated.</p>";
        }

        // Attach to DOM and animate in
        resultsSection.appendChild(clone);
        resultsSection.style.display = 'block';

        // Smooth scroll
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    async function fetchTrends() {
        try {
            const response = await fetch('/api/trends');
            const data = await response.json();

            if (data.status === 'success' && data.trends) {
                renderTrends(data.trends);
            }
        } catch (error) {
            console.error('Error fetching trends:', error);
        }
    }

    function renderTrends(trends) {
        trendsContainer.innerHTML = '';
        trends.forEach(trend => {
            const clone = trendTemplate.content.cloneNode(true);
            clone.querySelector('.trend-tag').textContent = trend.tag;
            clone.querySelector('h3').textContent = trend.title;
            clone.querySelector('p').textContent = trend.description;
            trendsContainer.appendChild(clone);
        });
    }
});
