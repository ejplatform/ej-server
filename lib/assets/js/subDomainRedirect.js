$(document).ready(function() {
  /*
   This script is responsible to help EJ to properly redirect
   the user, after login. The redirect will occurs always that the
   user is coming from some subdomain and wants to login. The user will
   login with the domain, and after login this script will redirect him
   to the stored subdomain.
  */
  sub_domain = window.location.search.replace(/.*=/, '');
  HTTP_OR_HTTPS_PATTERN = /^http(s)?.*/
  if (sub_domain && HTTP_OR_HTTPS_PATTERN.test(sub_domain)) {
    console.info("subdomain stored on localStorage");
    localStorage.setItem('sub_domain', sub_domain);
  }
  else{
    sub_domain = localStorage.getItem('sub_domain');
    if (sub_domain) {
      localStorage.removeItem('sub_domain');
      console.info("redirecting to subdomain...");
      window.location.replace(sub_domain);
    }
  }
});
