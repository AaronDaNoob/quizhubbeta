(function () {
  function loadBank() {
    fetch('quizzes.json', { cache: 'no-store' })
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function (bank) {
        if (!Array.isArray(bank)) throw new Error('Quiz bank must be an array');
        window.quizBank = bank.map(function (q) {
          if (!q || typeof q !== 'object') return q;
          return Object.assign({}, q, { cycle: q.cycle || 'chemistry' });
        });
        window.allQuizzes = window.quizBank.slice();
        if (typeof renderFilters === 'function') renderFilters();
        if (typeof renderQuizzes === 'function') renderQuizzes();
        if (typeof updateHeader === 'function') updateHeader();
        if (typeof updateFilterUI === 'function') updateFilterUI();
      })
      .catch(function (err) {
        console.warn('Could not load quiz bank:', err);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadBank, { once: true });
  } else {
    loadBank();
  }
})();
