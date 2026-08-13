/**
 * Keep the custom header navigation active state synchronised with
 * MkDocs Material instant navigation.
 *
 * Top-level items may group pages that do not share a URL prefix. Those
 * memberships are listed on data-nav-paths as site-root paths
 * (e.g. "cli/", "reference/config/"). Home stays exact-match only.
 */

(() => {
  "use strict";

  const { onDocumentReady, onInstantNavigation } =
    window.LupaxaPageLifecycle;

  const getSiteRootHref = () => {
    const home = document.querySelector(".lupaxa-header__nav-link");

    if (home?.href) {
      const url = new URL(home.href);
      let path = url.pathname.replace(/\/index\.html$/, "/");

      if (!path.endsWith("/")) {
        path += "/";
      }

      return `${url.origin}${path}`;
    }

    return `${window.location.origin}/`;
  };

  const normalisePath = (value, baseHref = window.location.href) => {
    const trimmed = String(value || "").trim();

    if (!trimmed || trimmed === ".") {
      return normalisePath(getSiteRootHref());
    }

    // Site-root docs paths from data-nav-paths: "cli/", "reference/config/"
    const base =
      trimmed.startsWith(".") ||
      trimmed.startsWith("/") ||
      trimmed.includes("://")
        ? baseHref
        : getSiteRootHref();

    const url = new URL(trimmed, base);
    const path = url.pathname
      .replace(/\/index\.html$/, "/")
      .replace(/\/+$/, "");

    return path || "/";
  };

  const pathMatches = (currentPath, candidate) => {
    const linkPath = normalisePath(candidate);

    return (
      currentPath === linkPath || currentPath.startsWith(`${linkPath}/`)
    );
  };

  const updateActiveNavigation = () => {
    const currentPath = normalisePath(window.location.href);
    const links = Array.from(
      document.querySelectorAll(".lupaxa-header__nav-link"),
    );

    if (!links.length) {
      return;
    }

    const homePath = normalisePath(links[0].href);

    links.forEach((link, index) => {
      const item = link.closest(".lupaxa-header__nav-item");

      if (!item) {
        return;
      }

      const isHome = index === 0;
      let isActive = false;

      if (isHome) {
        isActive = currentPath === homePath;
      } else {
        const declared = (link.getAttribute("data-nav-paths") || "")
          .trim()
          .split(/\s+/)
          .filter(Boolean);

        if (declared.length) {
          isActive = declared.some((candidate) =>
            pathMatches(currentPath, candidate),
          );
        } else {
          isActive = pathMatches(currentPath, link.href);
        }
      }

      item.classList.toggle("lupaxa-header__nav-item--active", isActive);

      if (isActive) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  };

  const scheduleUpdate = () => {
    requestAnimationFrame(updateActiveNavigation);
  };

  onDocumentReady(updateActiveNavigation);
  onInstantNavigation(updateActiveNavigation);

  window.addEventListener("popstate", scheduleUpdate);

  // Material also emits location$ on some navigations; subscribe if present.
  if (typeof location$ !== "undefined" && location$.subscribe) {
    location$.subscribe(scheduleUpdate);
  }
})();
