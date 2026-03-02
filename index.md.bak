---
layout: default
title: Home
---

<section class="hero" aria-label="Hero">
  <div class="hero__img" style="background-image:url('{{ '/assets/img/hero.jpg' | relative_url }}');"></div>
  <div class="hero__overlay"></div>
  <div class="hero__content">
    <h1 class="hero__title">キャッチコピーをここに</h1>
    <p class="hero__lead">
      研究概要（2〜3文程度）。この研究室が何を扱い、何が強みかを一般向けに。
    </p>
  </div>
</section>

<section class="section">
  <div class="section__title">
    <h2>Latest News</h2>
    <a href="{{ '/news/' | relative_url }}">See all →</a>
  </div>

  <div class="card">
    <div class="news-list">
      {% assign posts = site.posts | slice: 0, 6 %}
      {% for post in posts %}
        <div class="news-item">
          <div>
            <p class="news-item__title">
              <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
            </p>
          </div>
          <div class="news-item__meta">{{ post.date | date: "%Y-%m-%d" }}</div>
        </div>
      {% endfor %}
      {% if posts.size == 0 %}
        <div class="muted">まだニュースがありません。</div>
      {% endif %}
    </div>
  </div>
</section>
