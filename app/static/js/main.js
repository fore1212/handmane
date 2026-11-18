document.addEventListener('DOMContentLoaded', () => {
    const burgerBtn = document.getElementById('burgerBtn');
    const navMenu = document.getElementById('navMenu');
    if (burgerBtn && navMenu) {
        burgerBtn.addEventListener('click', () => navMenu.classList.toggle('open'));
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            const target = document.getElementById(btn.dataset.tab);
            if (target) target.classList.add('active');
        });
    });

    const openModalBtn = document.getElementById('openOrderModal');
    const closeModalBtn = document.getElementById('closeOrderModal');
    const orderModal = document.getElementById('orderModal');
    if (openModalBtn && orderModal) {
        openModalBtn.addEventListener('click', () => orderModal.classList.add('open'));
    }
    if (closeModalBtn && orderModal) {
        closeModalBtn.addEventListener('click', () => orderModal.classList.remove('open'));
    }

    const favBtn = document.getElementById('favBtn');
    if (favBtn) {
        favBtn.addEventListener('click', async () => {
            favBtn.disabled = true;
            try {
                const res = await fetch(favBtn.dataset.url);
                const data = await res.json();
                favBtn.textContent = data.liked ? '♥ В избранном' : '♡ Добавить в избранное';
            } finally {
                favBtn.disabled = false;
            }
        });
    }

    document.querySelectorAll('form[data-validate="true"]').forEach(form => {
        form.addEventListener('submit', e => {
            let hasError = false;
            form.querySelectorAll('[required]').forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#b85450';
                    hasError = true;
                } else {
                    field.style.borderColor = '';
                }
            });
            const priceInput = form.querySelector('input[name="price"]');
            if (priceInput && parseFloat(priceInput.value) <= 0) {
                alert('Цена должна быть больше нуля!');
                hasError = true;
            }
            if (hasError) e.preventDefault();
        });
    });
});
