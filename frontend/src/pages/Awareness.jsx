import { useMemo, useState } from 'react';
import { BookOpen, CheckCircle2, ChevronDown, ChevronUp, GraduationCap, Search } from 'lucide-react';
import { awarenessService } from '../api/services';
import { useFetch } from '../hooks/useFetch';
import PageHeader from '../components/PageHeader';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import AdvisoryNote from '../components/AdvisoryNote';

export default function Awareness() {
  const { data, loading, error, reload } = useFetch(awarenessService.list, []);
  const [query, setQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [expanded, setExpanded] = useState({});

  const categories = Array.isArray(data?.categories) ? data.categories : [];

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return categories
      .map((category) => {
        const articles = (Array.isArray(category.articles) ? category.articles : []).filter((article) => {
          if (!needle) return true;
          const haystack = [
            article.title,
            article.summary,
            ...(Array.isArray(article.content) ? article.content : []),
            ...(Array.isArray(article.checklist) ? article.checklist : []),
          ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase();
          return haystack.includes(needle);
        });
        return { ...category, articles };
      })
      .filter((category) => category.articles.length > 0)
      .filter((category) => activeCategory === 'all' || category.id === activeCategory);
  }, [categories, query, activeCategory]);

  const articleCount = filtered.reduce((sum, category) => sum + category.articles.length, 0);
  const hasFilters = Boolean(query.trim()) || activeCategory !== 'all';

  return (
    <>
      <PageHeader
        eyebrow="Scam awareness"
        title="Short guides to common scams"
        description="Plain-language explanations and simple checklists you can share with the people you care about."
      />

      {loading ? (
        <div className="fs-card"><LoadingState label="Loading guides…" /></div>
      ) : error ? (
        <div className="fs-card"><ErrorState error={error} onRetry={reload} title="Could not load awareness guides" /></div>
      ) : categories.length === 0 ? (
        <div className="fs-card"><EmptyState icon={GraduationCap} title="No guides available" description="Guides will appear here once they are published." /></div>
      ) : (
        <>
          <div className="fs-card mb-5 p-4 sm:p-5">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search guides and checklists"
                aria-label="Search awareness guides"
                className="fs-input pl-10 text-[13px]"
              />
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => setActiveCategory('all')}
                className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                  activeCategory === 'all' ? 'bg-navy-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
                aria-pressed={activeCategory === 'all'}
              >
                All topics
              </button>
              {categories.map((category) => (
                <button
                  key={category.id}
                  type="button"
                  onClick={() => setActiveCategory(category.id)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                    activeCategory === category.id ? 'bg-navy-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                  aria-pressed={activeCategory === category.id}
                >
                  {category.title}
                </button>
              ))}
            </div>
            {articleCount > 0 && (
              <p className="mt-3 text-[11px] text-slate-400">Showing {articleCount} {articleCount === 1 ? 'guide' : 'guides'}</p>
            )}
          </div>

          {filtered.length === 0 ? (
            <div className="fs-card">
              <EmptyState
                icon={Search}
                title="No guides match your search"
                description="Try a different word, or choose All topics."
                action={
                  hasFilters ? (
                    <button
                      type="button"
                      className="fs-btn-secondary"
                      onClick={() => {
                        setQuery('');
                        setActiveCategory('all');
                      }}
                    >
                      Clear filters
                    </button>
                  ) : undefined
                }
              />
            </div>
          ) : (
            <div className="space-y-7">
              {filtered.map((category) => (
                <section key={category.id}>
                  <div className="mb-3.5 flex items-start gap-3">
                    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-700">
                      <BookOpen className="h-[18px] w-[18px]" strokeWidth={1.8} />
                    </span>
                    <div>
                      <h2 className="text-base font-semibold tracking-tight text-slate-900">{category.title}</h2>
                      {category.description && <p className="mt-0.5 text-sm text-slate-500">{category.description}</p>}
                    </div>
                  </div>

                  <div className="grid gap-4 lg:grid-cols-2">
                    {(category.articles || []).map((article) => {
                      const key = `${category.id}-${article.id}`;
                      const isOpen = Boolean(expanded[key]);
                      return (
                        <article key={key} className="fs-card overflow-hidden">
                          <div className="p-5 sm:p-6">
                            <h3 className="text-sm font-semibold text-slate-900">{article.title}</h3>
                            {article.summary && <p className="mt-2 text-sm leading-relaxed text-slate-500">{article.summary}</p>}

                            {isOpen && (
                              <div className="mt-5 animate-fade-in border-t border-line pt-5">
                                <div className="max-w-prose space-y-3">
                                  {(article.content || []).map((paragraph, index) => (
                                    <p key={`${key}-p-${index}`} className="text-[13px] leading-7 text-slate-600">
                                      {paragraph}
                                    </p>
                                  ))}
                                </div>

                                {Array.isArray(article.checklist) && article.checklist.length > 0 && (
                                  <div className="mt-5 rounded-xl border border-emerald-100 bg-emerald-50/50 p-4">
                                    <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-emerald-800">Quick checklist</p>
                                    <ul className="space-y-2.5">
                                      {article.checklist.map((item, index) => (
                                        <li key={`${key}-c-${index}`} className="flex items-start gap-2.5 text-[13px] leading-relaxed text-slate-700">
                                          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" strokeWidth={1.9} />
                                          <span>{item}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={() => setExpanded((current) => ({ ...current, [key]: !current[key] }))}
                            className="flex w-full items-center justify-between border-t border-line bg-slate-50/60 px-5 py-3 text-xs font-semibold text-navy-800 transition hover:bg-slate-100 sm:px-6"
                            aria-expanded={isOpen}
                          >
                            {isOpen ? 'Show less' : 'Read this guide'}
                            {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                          </button>
                        </article>
                      );
                    })}
                  </div>
                </section>
              ))}
            </div>
          )}

          <AdvisoryNote className="mt-7" />
        </>
      )}
    </>
  );
}
