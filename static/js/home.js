// 一般視覺動畫用 CSS；逐字／逐詞與捲動路線用 Anime.js。
(() => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let playSectionText = () => {};

  // 區塊進入畫面時加上類別，離開時移除；再次進入便會重播 CSS 動畫。
  if (!reduceMotion.matches && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const section = entry.target;

        if (!entry.isIntersecting) {
          section.classList.remove('is-visible');
          return;
        }

        if (section.classList.contains('is-visible')) return;

        section.classList.add('is-visible');
        playSectionText(section);
      });
    }, { threshold: 0.16 });

    document.querySelectorAll('[data-reveal]').forEach((section) => {
      observer.observe(section);
    });
  }

  // 尊重系統的「減少動態效果」設定。
  if (reduceMotion.matches) return;

  function startAnimations() {
    const { animate, onScroll, splitText, stagger } = window.anime;
    const textEffects = new WeakMap();

    // 只切分一次文字；之後上下滑動時重播同一組字／詞，不重複增加 span。
    document.querySelectorAll('[data-text-animate]').forEach((element) => {
      const mode = element.dataset.textAnimate;
      const byWords = mode === 'words';
      const split = splitText(element, {
        words: byWords,
        chars: !byWords,
        accessible: true,
      });
      const pieces = byWords ? split.words : split.chars;
      // 整段文字開始前要等多久（毫秒）；數值來自 HTML 的 data-text-delay。
      const startDelay = Number(element.dataset.textDelay || 0);

      textEffects.set(element, () => {
        animate(pieces, {
          opacity: [0, 1],
          y: [byWords ? 12 : 18, 0],
          // 詞與詞相隔 55ms、字與字相隔 38ms；調大會讓文字更慢地依序出現。
          delay: stagger(byWords ? 55 : 60, { start: startDelay }),
          // 每個字／詞從開始到完成需 650ms；調大會讓個別字／詞移動得更慢。
          duration: 650,
          ease: 'out(3)',
        });
      });
    });

    playSectionText = (section) => {
      section.querySelectorAll('[data-text-animate]').forEach((element) => {
        textEffects.get(element)?.();
      });
    };

    playSectionText(document.querySelector('.hero'));

    // Anime.js 若比觀察器稍晚載入，補播已經進入畫面的標題。
    document.querySelectorAll('[data-reveal].is-visible').forEach(playSectionText);

    const journey = document.getElementById('journey');
    if (!journey) return;

    // 路線長度與捲動位置同步，沒有固定播放時長；捲得快就變化得快。
    animate('.journey-progress', {
      height: ['0%', '100%'],
      ease: 'linear',
      autoplay: onScroll({
        target: journey,
        enter: 'bottom top',
        leave: 'top bottom',
        sync: true,
      }),
    });
  }

  if (window.anime) {
    startAnimations();
    return;
  }
})();
