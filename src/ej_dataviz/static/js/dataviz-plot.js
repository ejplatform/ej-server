/**
 * Initialize *magical js table lib* for all elements marked as <table dynamic>
 */
up.compile('table[dynamic]', function ($elem) {
    console.log($elem);
});
