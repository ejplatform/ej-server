$(document).ready(function() {
  custom_domain = window.location.search.replace(/.*=/, '');
  if (custom_domain && /^(http)?(https)?.*/.test(custom_domain)) {
    localStorage.setItem('custom_domain', custom_domain);
  }
  else{
    custom_domain = localStorage.getItem('custom_domain');
    if (custom_domain) {
      localStorage.removeItem('custom_domain');
      window.location.replace(custom_domain);
    }
  }
});
