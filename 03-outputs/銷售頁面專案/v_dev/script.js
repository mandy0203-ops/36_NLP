document.addEventListener('DOMContentLoaded', function () {
    const reveals = document.querySelectorAll('.reveal');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    });

    reveals.forEach((reveal) => {
        observer.observe(reveal);
    });
});

function toggleFaq(element) {
    const item = element.parentElement;
    const answer = item.querySelector('.faq-a');
    const icon = element.querySelector('span i');

    // Close others
    const allAnswers = document.querySelectorAll('.faq-a');
    allAnswers.forEach(a => {
        if (a !== answer) a.style.display = 'none';
    });
    const allIcons = document.querySelectorAll('.faq-q span i');
    allIcons.forEach(i => {
        if (i !== icon) i.classList.replace('fa-minus', 'fa-plus');
    });

    if (answer.style.display === 'block') {
        answer.style.display = 'none';
        icon.classList.replace('fa-minus', 'fa-plus');
    } else {
        answer.style.display = 'block';
        icon.classList.replace('fa-plus', 'fa-minus');
    }
}
