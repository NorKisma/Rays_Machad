// Side bar toggle logic
document.addEventListener('DOMContentLoaded', function () {
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(reg => console.log('Service Worker Registered'))
                .catch(err => console.log('Service Worker Failed', err));
        });
    }

    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            const isOpen = sidebar.classList.toggle('sidebar-open');
            if (backdrop) {
                if (isOpen) {
                    document.body.style.overflow = 'hidden';
                    backdrop.style.display = 'block';
                    // Force reflow
                    backdrop.offsetHeight;
                    backdrop.classList.add('show');
                } else {
                    document.body.style.overflow = '';
                    backdrop.classList.remove('show');
                    setTimeout(() => {
                        if (!sidebar.classList.contains('sidebar-open')) {
                            backdrop.style.display = 'none';
                        }
                    }, 300);
                }
            }
        });
    }

    if (backdrop && sidebar) {
        const closeBtn = document.getElementById('sidebarClose');
        const hideSidebar = function () {
            sidebar.classList.remove('sidebar-open');
            backdrop.classList.remove('show');
            document.body.style.overflow = '';
            setTimeout(() => {
                if (!sidebar.classList.contains('sidebar-open')) {
                    backdrop.style.display = 'none';
                }
            }, 300);
        };

        backdrop.addEventListener('click', hideSidebar);
        if (closeBtn) {
            closeBtn.addEventListener('click', hideSidebar);
        }
    }

    // Theme toggle logic
    // Theme toggle logic
    const themeToggles = document.querySelectorAll('#themeToggle, #themeToggleMobile');
    const htmlEl = document.documentElement;

    function updateThemeIcons(theme) {
        document.querySelectorAll('.theme-icon-light').forEach(icon => {
            theme === 'dark' ? icon.classList.remove('d-none') : icon.classList.add('d-none');
        });
        document.querySelectorAll('.theme-icon-dark').forEach(icon => {
            theme === 'dark' ? icon.classList.add('d-none') : icon.classList.remove('d-none');
        });
    }

    // Set initial icons
    updateThemeIcons(htmlEl.getAttribute('data-theme'));

    themeToggles.forEach(toggle => {
        toggle.addEventListener('click', function () {
            const currentTheme = htmlEl.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            htmlEl.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcons(newTheme);
        });
    });

    // Sidebar Scroll Management: Ensure active item is visible on load
    const activeLink = sidebar.querySelector('.nav-link.active');
    if (activeLink) {
        setTimeout(() => {
            const linkOffsetTop = activeLink.offsetTop;
            sidebar.scrollTo({
                top: linkOffsetTop - 100,
                behavior: 'instant'
            });
        }, 100);
    }

    // Sidebar Scroll Management: Ensure sub-menus are visible when expanded
    // This targets ALL collapsing elements inside the sidebar for maximum reliability
    $('#sidebar .collapse').on('show.bs.collapse', function () {
        const $el = $(this);
        const $parentLi = $el.closest('.nav-item');
        const $sidebar = $('#sidebar');

        if ($parentLi.length && $sidebar.length) {
            // Short delay to allow the animation to start and position to stabilize
            setTimeout(() => {
                // Calculate position relative to the sidebar container
                const currentScroll = $sidebar.scrollTop();
                const elementTop = $parentLi.position().top; // Relative to offsetParent (sidebar)

                $sidebar.animate({
                    scrollTop: currentScroll + elementTop - 15  // Scroll to item top with a small margin
                }, 400);
            }, 150);
        }
    });

    // Initialize Select2 on all dropdowns
    // Use jQuery for Select2 initialization as required by the library
    try {
        if ($('select').length > 0) {
            $('select').select2({
                theme: 'bootstrap-5',
                width: '100%',
                placeholder: 'Select an option',
                allowClear: true,
                dir: document.documentElement.dir || 'ltr'
            });
        }
    } catch (e) {
        console.error('Select2 initialization failed:', e);
    }

    // Global DataTables Initialization
    const initAllDataTables = () => {
        if (!$.fn.DataTable) {
            console.error('DataTables library not loaded!');
            return;
        }

        const initializeDataTable = (table) => {
            const $table = $(table);
            if ($.fn.DataTable.isDataTable($table) || $table.hasClass('no-datatable')) return;

            try {
                const config = {
                    pageLength: $table.data('page-length') || 10,
                    lengthMenu: [[10, 25, 50, 100, 150, 200, 300, -1], [10, 25, 50, 100, 150, 200, 300, "All"]],
                    ordering: $table.data('ordering') !== false,
                    searching: $table.data('searching') !== false,
                    paging: $table.data('paging') !== false,
                    info: $table.data('info') !== false,
                    language: window.datatables_translations || {},
                    responsive: true,
                    dom: $table.data('dom') || '<"row align-items-center mb-3"<"col-md-6 d-flex align-items-center gap-3"lB><"col-md-6"f>>t<"row align-items-center mt-3 pt-3 border-top"<"col-md-6"i><"col-md-6"p>>',
                    buttons: [
                        { extend: 'copy', className: 'btn btn-sm btn-light border px-3 fw-bold' },
                        { extend: 'excel', className: 'btn btn-sm btn-light border px-3 fw-bold text-success' },
                        { extend: 'pdf', className: 'btn btn-sm btn-light border px-3 fw-bold text-danger' },
                        { extend: 'print', className: 'btn btn-sm btn-light border px-3 fw-bold text-primary' }
                    ],
                    order: (function () {
                        const d = $table.attr('data-order');
                        try { return d ? JSON.parse(d) : []; } catch (e) { return []; }
                    })()
                };

                // Report/Financial specific layout
                if ($table.hasClass('financial-table') || $table.parents('.printable-section').length) {
                    config.ordering = false;
                    config.dom = '<"row align-items-center mb-4 no-print"<"col-md-6"lf><"col-md-6 text-end"B>>t<"row align-items-center mt-4 no-print"<"col-md-6"i><"col-md-6"p>>';
                }

                const dt = $table.DataTable(config);

                // Sync with header search immediately
                const currentSearch = $('#headerSearchInput').val();
                if (currentSearch) dt.search(currentSearch).draw();

            } catch (err) {
                console.error('Failed to initialize individual DataTable:', err, table);
            }
        };

        $('table:not(.no-datatable)').each(function () {
            initializeDataTable(this);
        });
    };

    // Run initialization
    $(document).ready(initAllDataTables);

    // UNIFIED Global Search Listener (Targets ALL tables at once)
    const headerSearchInput = $('#headerSearchInput');
    if (headerSearchInput.length > 0) {
        headerSearchInput.off('keyup input').on('keyup input', function () {
            const val = this.value;
            if ($.fn.DataTable) {
                $.fn.dataTable.tables({ api: true }).search(val).draw();
            }
        });

        $(document).on('keydown', function (e) {
            if ((e.ctrlKey && e.key === 'k') || (e.key === '/' && !$(e.target).is('input, textarea'))) {
                e.preventDefault();
                headerSearchInput.focus().select();
            }
        });
    }

    // Tab adjustment
    $('a[data-bs-toggle="tab"], button[data-bs-toggle="tab"]').on('shown.bs.tab', function () {
        if ($.fn.DataTable) {
            $($.fn.dataTable.tables(true)).DataTable().columns.adjust().responsive.recalc();
        }
    });

    // Bi-directional search sync
    $(document).on('search.dt', function (e, settings) {
        const api = new $.fn.dataTable.Api(settings);
        const searchVal = api.search();
        const $headerSearch = $('#headerSearchInput');
        if ($headerSearch.length > 0 && document.activeElement !== $headerSearch[0]) {
            $headerSearch.val(searchVal);
        }
    });
});
