const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.panel');
tabs.forEach(t => t.addEventListener('click', () => {
  tabs.forEach(x => x.classList.remove('active'));
  panels.forEach(p => p.classList.remove('active'));
  t.classList.add('active');
  document.querySelector(t.dataset.target).classList.add('active');
}));

// Simple front-end validation: ensure at least one input is present before submit
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', (e) => {
    const urlInput = form.querySelector('input[type="url"]');
    const fileInput = form.querySelector('input[type="file"]');
    if (urlInput && !urlInput.value) return; // allow server to validate if filled
    if (fileInput && (!fileInput.files || fileInput.files.length === 0)) {
      e.preventDefault();
      alert('Please choose a PDF file.');
    }
  });
});

