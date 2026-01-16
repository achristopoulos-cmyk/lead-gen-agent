/**
 * Rock Salt Lead Capture Popup
 *
 * Best Practice Triggers:
 * - Exit intent (mouse leaves viewport)
 * - Time on page (30 seconds)
 * - Scroll depth (50% of page)
 * - Only shows once per session
 * - Remembers dismissals for 7 days
 *
 * Usage: Add this script to any page:
 * <script src="https://your-domain.com/popup-form.js"></script>
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        webhookUrl: 'https://lead-gen-agent-2qmw.onrender.com/webhook/lead',
        cookieName: 'rs_popup_dismissed',
        cookieDays: 7,
        timeDelay: 30000,        // 30 seconds on page
        scrollDepth: 50,         // 50% scroll depth
        exitIntentEnabled: true,
        timeDelayEnabled: true,
        scrollDepthEnabled: true,
        mobileEnabled: true,     // Show on mobile too
        debug: false
    };

    // Check if already dismissed
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/`;
    }

    // Don't show if already dismissed
    if (getCookie(CONFIG.cookieName)) {
        if (CONFIG.debug) console.log('[Popup] Already dismissed, not showing');
        return;
    }

    // Don't show if already shown this session
    if (sessionStorage.getItem('rs_popup_shown')) {
        if (CONFIG.debug) console.log('[Popup] Already shown this session');
        return;
    }

    let popupShown = false;

    // Create and inject styles
    const styles = `
        .rs-popup-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            z-index: 999998;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
        }

        .rs-popup-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .rs-popup-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.9);
            background: white;
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
            z-index: 999999;
            width: 90%;
            max-width: 440px;
            max-height: 90vh;
            overflow-y: auto;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s, transform 0.3s;
        }

        .rs-popup-container.active {
            opacity: 1;
            visibility: visible;
            transform: translate(-50%, -50%) scale(1);
        }

        .rs-popup-close {
            position: absolute;
            top: 12px;
            right: 12px;
            width: 32px;
            height: 32px;
            border: none;
            background: #f7fafc;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
            z-index: 1;
        }

        .rs-popup-close:hover {
            background: #edf2f7;
        }

        .rs-popup-close svg {
            width: 16px;
            height: 16px;
            color: #718096;
        }

        .rs-popup-content {
            padding: 32px;
        }

        .rs-popup-header {
            text-align: center;
            margin-bottom: 24px;
        }

        .rs-popup-header h2 {
            color: #1a202c;
            font-size: 24px;
            font-weight: 700;
            margin: 0 0 8px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .rs-popup-header p {
            color: #718096;
            font-size: 15px;
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .rs-popup-form .form-group {
            margin-bottom: 16px;
        }

        .rs-popup-form .form-row {
            display: flex;
            gap: 12px;
        }

        .rs-popup-form .form-row .form-group {
            flex: 1;
        }

        .rs-popup-form label {
            display: block;
            color: #4a5568;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 4px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .rs-popup-form input,
        .rs-popup-form select {
            width: 100%;
            padding: 10px 14px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 15px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            transition: border-color 0.2s, box-shadow 0.2s;
            background: white;
            box-sizing: border-box;
        }

        .rs-popup-form input:focus,
        .rs-popup-form select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .rs-popup-form input::placeholder {
            color: #a0aec0;
        }

        .rs-popup-form select {
            cursor: pointer;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23718096' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
            background-size: 14px;
        }

        .rs-popup-form button {
            width: 100%;
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .rs-popup-form button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -10px rgba(102, 126, 234, 0.5);
        }

        .rs-popup-form button:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }

        .rs-popup-success {
            display: none;
            text-align: center;
            padding: 20px 0;
        }

        .rs-popup-success svg {
            width: 56px;
            height: 56px;
            color: #48bb78;
            margin-bottom: 12px;
        }

        .rs-popup-success h3 {
            color: #1a202c;
            font-size: 20px;
            margin: 0 0 8px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .rs-popup-success p {
            color: #718096;
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .rs-popup-error {
            background: #fed7d7;
            color: #c53030;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 16px;
            display: none;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .rs-popup-privacy {
            text-align: center;
            margin-top: 16px;
            font-size: 12px;
            color: #a0aec0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        @media (max-width: 480px) {
            .rs-popup-form .form-row {
                flex-direction: column;
                gap: 0;
            }

            .rs-popup-content {
                padding: 24px;
            }

            .rs-popup-header h2 {
                font-size: 20px;
            }
        }
    `;

    // Create and inject HTML
    const html = `
        <div class="rs-popup-overlay" id="rs-popup-overlay"></div>
        <div class="rs-popup-container" id="rs-popup-container">
            <button class="rs-popup-close" id="rs-popup-close" aria-label="Close">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
            <div class="rs-popup-content">
                <div class="rs-popup-header">
                    <h2>Before you go...</h2>
                    <p>Get actionable tools to grow your business</p>
                </div>

                <div class="rs-popup-error" id="rs-popup-error"></div>

                <form class="rs-popup-form" id="rs-popup-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="rs-first-name">First Name</label>
                            <input type="text" id="rs-first-name" name="first_name" placeholder="Jane" required>
                        </div>
                        <div class="form-group">
                            <label for="rs-last-name">Last Name</label>
                            <input type="text" id="rs-last-name" name="last_name" placeholder="Smith" required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="rs-email">Email</label>
                        <input type="email" id="rs-email" name="email" placeholder="jane@company.com" required>
                    </div>

                    <div class="form-group">
                        <label for="rs-company">Company</label>
                        <input type="text" id="rs-company" name="company" placeholder="Your company" required>
                    </div>

                    <div class="form-group">
                        <label for="rs-title">Job Title</label>
                        <input type="text" id="rs-title" name="title" placeholder="CEO, Founder, etc.">
                    </div>

                    <div class="form-group">
                        <label for="rs-interest">I'm interested in...</label>
                        <select id="rs-interest" name="interested_in" required>
                            <option value="" disabled selected>Select...</option>
                            <option value="linkedin_presence">LinkedIn Presence - Join the Zag</option>
                            <option value="customer_voice_research">Customer Voice Research</option>
                            <option value="both">Both / Not sure yet</option>
                        </select>
                    </div>

                    <button type="submit" id="rs-popup-submit">Get Started Free</button>
                </form>

                <div class="rs-popup-success" id="rs-popup-success">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3>You're in!</h3>
                    <p>Check your inbox - we'll be in touch soon.</p>
                </div>

                <p class="rs-popup-privacy">We respect your privacy. Unsubscribe anytime.</p>
            </div>
        </div>
    `;

    // Inject styles
    const styleEl = document.createElement('style');
    styleEl.textContent = styles;
    document.head.appendChild(styleEl);

    // Inject HTML
    const wrapper = document.createElement('div');
    wrapper.innerHTML = html;
    document.body.appendChild(wrapper);

    // Get elements
    const overlay = document.getElementById('rs-popup-overlay');
    const container = document.getElementById('rs-popup-container');
    const closeBtn = document.getElementById('rs-popup-close');
    const form = document.getElementById('rs-popup-form');
    const errorEl = document.getElementById('rs-popup-error');
    const successEl = document.getElementById('rs-popup-success');
    const submitBtn = document.getElementById('rs-popup-submit');

    // Show popup
    function showPopup(trigger) {
        if (popupShown) return;
        popupShown = true;
        sessionStorage.setItem('rs_popup_shown', 'true');

        if (CONFIG.debug) console.log('[Popup] Showing popup, trigger:', trigger);

        overlay.classList.add('active');
        container.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    // Hide popup
    function hidePopup(dismissed = false) {
        overlay.classList.remove('active');
        container.classList.remove('active');
        document.body.style.overflow = '';

        if (dismissed) {
            setCookie(CONFIG.cookieName, 'true', CONFIG.cookieDays);
            if (CONFIG.debug) console.log('[Popup] Dismissed, setting cookie');
        }
    }

    // Close handlers
    closeBtn.addEventListener('click', () => hidePopup(true));
    overlay.addEventListener('click', () => hidePopup(true));

    // ESC key closes popup
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && container.classList.contains('active')) {
            hidePopup(true);
        }
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        errorEl.style.display = 'none';

        const data = {
            first_name: document.getElementById('rs-first-name').value,
            last_name: document.getElementById('rs-last-name').value,
            email: document.getElementById('rs-email').value,
            company: document.getElementById('rs-company').value,
            title: document.getElementById('rs-title').value,
            interested_in: document.getElementById('rs-interest').value,
            source: 'popup_form'
        };

        try {
            const response = await fetch(CONFIG.webhookUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                form.style.display = 'none';
                successEl.style.display = 'block';
                setCookie(CONFIG.cookieName, 'converted', CONFIG.cookieDays * 4); // Remember longer for conversions

                // Auto close after 3 seconds
                setTimeout(() => hidePopup(false), 3000);
            } else {
                throw new Error('Submission failed');
            }
        } catch (error) {
            errorEl.textContent = 'Something went wrong. Please try again.';
            errorEl.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.textContent = 'Get Started Free';
        }
    });

    // === TRIGGER: Exit Intent ===
    if (CONFIG.exitIntentEnabled) {
        let exitIntentTriggered = false;

        document.addEventListener('mouseout', (e) => {
            if (exitIntentTriggered || popupShown) return;

            // Check if mouse left through top of viewport (closing tab/leaving)
            if (e.clientY < 10 && e.relatedTarget === null) {
                exitIntentTriggered = true;
                showPopup('exit_intent');
            }
        });
    }

    // === TRIGGER: Time on Page ===
    if (CONFIG.timeDelayEnabled) {
        setTimeout(() => {
            if (!popupShown) {
                showPopup('time_delay');
            }
        }, CONFIG.timeDelay);
    }

    // === TRIGGER: Scroll Depth ===
    if (CONFIG.scrollDepthEnabled) {
        let scrollTriggered = false;

        window.addEventListener('scroll', () => {
            if (scrollTriggered || popupShown) return;

            const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;

            if (scrollPercent >= CONFIG.scrollDepth) {
                scrollTriggered = true;
                showPopup('scroll_depth');
            }
        });
    }

    if (CONFIG.debug) console.log('[Popup] Initialized with config:', CONFIG);

})();
