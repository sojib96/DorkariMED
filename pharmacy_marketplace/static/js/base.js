// Base JavaScript — shared across all surfaces

document.addEventListener('DOMContentLoaded', function () {

  // ── OTP Digit Input Auto-Advance ──────────────────────────────────────────
  function initOtpInput(container) {
    const boxes = container.querySelectorAll('.otp-box');
    if (!boxes.length) return;

    boxes.forEach((box, index) => {
      // Input: only allow single digit, auto-advance
      box.addEventListener('input', function (e) {
        const val = this.value.replace(/[^0-9]/g, '');
        this.value = val.slice(0, 1);
        if (val && index < boxes.length - 1) {
          boxes[index + 1].focus();
        }
        updateFilledState(container);
        checkAutoSubmit(container);
      });

      // Keydown: handle backspace to go to previous box
      box.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !this.value && index > 0) {
          boxes[index - 1].focus();
        }
        if (e.key === 'ArrowLeft' && index > 0) {
          boxes[index - 1].focus();
        }
        if (e.key === 'ArrowRight' && index < boxes.length - 1) {
          boxes[index + 1].focus();
        }
      });

      // Focus: select contents
      box.addEventListener('focus', function () {
        this.select();
      });

      // Paste: fill all 6 digits
      box.addEventListener('paste', function (e) {
        e.preventDefault();
        const paste = (e.clipboardData || window.clipboardData).getData('text');
        const digits = paste.replace(/[^0-9]/g, '').slice(0, boxes.length);
        digits.split('').forEach((digit, i) => {
          if (boxes[i]) boxes[i].value = digit;
        });
        updateFilledState(container);
        checkAutoSubmit(container);
        if (digits.length === boxes.length) {
          boxes[boxes.length - 1].focus();
        } else if (digits.length) {
          boxes[Math.min(digits.length, boxes.length - 1)].focus();
        }
      });
    });
  }

  function updateFilledState(container) {
    container.querySelectorAll('.otp-box').forEach(box => {
      box.classList.toggle('filled', box.value.length > 0);
      box.classList.remove('error');
    });
  }

  function checkAutoSubmit(container) {
    const boxes = container.querySelectorAll('.otp-box');
    const allFilled = Array.from(boxes).every(b => b.value.length === 1);
    const form = container.closest('form');
    if (allFilled && form) {
      // Debounce 300ms then submit
      clearTimeout(container._otpTimer);
      container._otpTimer = setTimeout(() => {
        form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      }, 300);
    }
  }

  // Initialize OTP on page load and after htmx swaps
  document.querySelectorAll('.otp-input-group').forEach(initOtpInput);
  document.addEventListener('htmx:afterSwap', function (e) {
    e.detail.target.querySelectorAll('.otp-input-group').forEach(initOtpInput);
  });

  // ── Password Show/Hide Toggle ─────────────────────────────────────────────
  document.querySelectorAll('.password-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const input = this.closest('.password-wrapper').querySelector('.input');
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      this.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
      // Update icon: eye / eye-off (simple SVG toggle)
      const icon = this.querySelector('svg');
      if (icon) {
        icon.innerHTML = isPassword
          ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>'
          : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>';
      }
    });
  });

  // ── Alert Auto-Dismiss ────────────────────────────────────────────────────
  document.querySelectorAll('.alert[data-auto-dismiss]').forEach(function (alert) {
    const seconds = parseInt(alert.getAttribute('data-auto-dismiss'), 10) || 5000;
    setTimeout(function () {
      alert.style.transition = 'opacity 0.3s';
      alert.style.opacity = '0';
      setTimeout(function () { alert.remove(); }, 300);
    }, seconds);
  });

  // ── Form loading state on htmx submit ─────────────────────────────────────
  document.addEventListener('htmx:beforeRequest', function (e) {
    const form = e.detail.elt.closest('form');
    if (form) {
      const btn = form.querySelector('button[type="submit"], .btn[type="submit"]');
      if (btn && !btn.disabled) {
        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.dataset.originalText = originalText;
        btn.innerHTML = '<span class="spinner"></span> ' + (btn.dataset.loadingText || 'Processing...');
      }
    }
  });

  document.addEventListener('htmx:afterRequest', function (e) {
    const form = e.detail.elt.closest('form');
    if (form) {
      const btn = form.querySelector('button[type="submit"], .btn[type="submit"]');
      if (btn && btn.dataset.originalText) {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalText;
        delete btn.dataset.originalText;
      }
    }
  });

  // ── htmx error handler ────────────────────────────────────────────────────
  document.addEventListener('htmx:responseError', function (e) {
    const target = e.detail.target;
    if (target && !target.querySelector('.alert-error')) {
      const errorDiv = document.createElement('div');
      errorDiv.className = 'alert alert-error';
      errorDiv.setAttribute('role', 'alert');
      errorDiv.innerHTML = '<span class="alert-icon">⚠</span><span class="alert-body">Connection lost. Please check your internet and try again.</span>';
      target.prepend(errorDiv);
    }
  });

  // ── Multi-step form: store step data ──────────────────────────────────────
  // Handled server-side via Django session; this listens for step transitions
  document.addEventListener('htmx:afterSwap', function (e) {
    // Re-run OTP init for any new OTP groups in swapped content
    e.detail.target.querySelectorAll('.otp-input-group').forEach(initOtpInput);
  });

  // ── CSRF token setup for htmx ────────────────────────────────────────────
  document.addEventListener('htmx:configRequest', function (e) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
      e.detail.headers['X-CSRFToken'] = csrfToken.value;
    }
  });

  // ── HTMX form validation (HTML5 + custom) ────────────────────────────────
  document.addEventListener('htmx:validateForm', function (e) {
    const form = e.detail.elt;
    if (form && !form.checkValidity()) {
      e.detail.shouldProceed = false;
      form.reportValidity();
    }
  });
});
