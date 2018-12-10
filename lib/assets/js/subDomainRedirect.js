$(document).ready(function() {
  custom_domain = window.location.search.replace(/.*=/, '');
  if (custom_domain && /^http(s)?.*/.test(custom_domain)) {
    console.info("custom domain stored on localStorage");
    localStorage.setItem('custom_domain', custom_domain);
  }
  else{
    custom_domain = localStorage.getItem('custom_domain');
    if (custom_domain) {
      localStorage.removeItem('custom_domain');
      console.info("redirecting to custom domain...");
      window.location.replace(custom_domain);
    }
  }
});
