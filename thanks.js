<script>
  // Year in footer
  document.getElementById('yr').textContent = new Date().getFullYear();

  // Compose a mailto so the comment comes to your Gmail
  const form = document.getElementById('commentForm');
  form.addEventListener('submit', function(e){
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const fromEmail = document.getElementById('email').value.trim();
    const subject = document.getElementById('subject').value.trim() || 'Website Comment';
    const msg = document.getElementById('message').value.trim();

    const lines = [
      `Name: ${name}`,
      `Reply-To: ${fromEmail}`,
      '',
      msg
    ].join('\n');

    const mailto = `mailto:benayasleulseged@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines)}`;
    // Open default email client
    window.location.href = mailto;

    // Show helper text
    const ok = document.getElementById('ok');
    ok.style.display = 'block';
  });
</script>
