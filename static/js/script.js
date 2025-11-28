document.addEventListener('DOMContentLoaded', function() {
    // بيانات الترجمة
    const translations = {
        en: {
            // Navigation
            'lotus': 'Lotus',
            'nav-products': 'Products',
            'nav-services': 'Services',
            'nav-company': 'Company',
            'nav-about': 'About',
            'nav-contact': 'Contact',
            'nav-team': 'Executive Team',
            'nav-news': 'Newsroom',
            'nav-careers': 'Careers',
            'nav-industries': 'Industries',
            'nav-resources': 'Resources',
            'nav-design': 'Design Your Tool',
            'nav-buy': 'Buy',
            'nav-demo': 'Request a Demo',
            'search-placeholder': 'Search research, analysis, tools...',
            
            // Hero section
            'hero-title': 'Explore Lotus',
            'hero-subtitle': 'AI-powered platform for researchers and academics to analyze qualitative and quantitative data with precision',
            'cta-primary': 'Begin Analysis',
            'cta-secondary': 'Design Your Tool',
            
            // Products Section
            'products': 'Our Products',
            'feature1-title': 'Advanced AI-Powered Analysis Tools',
            'feature1-desc': 'Lotus Platform offers comprehensive qualitative and quantitative data analysis with cutting-edge AI algorithms and natural language processing.',
            'feature1-item1': 'Dual language support (Arabic & English)',
            'feature1-item2': 'Multi-format data processing',
            'feature1-item3': 'Automated insights and visualization',
            'learn-more': 'Explore all products',
            
            // Services Section
            'services': 'Our Services',
            'feature2-title': 'Comprehensive Research Support',
            'feature2-desc': 'We provide end-to-end services from data collection to analysis and visualization for academic and professional research teams.',
            'feature2-item1': 'Custom tool development',
            'feature2-item2': 'Research consultation',
            'feature2-item3': 'Data visualization services',
            'learn-more2': 'Discover our services',
            
            // Industries Section
            'industries': 'Industries',
            'feature3-title': 'Serving Diverse Sectors',
            'feature3-desc': 'Our platform supports researchers and analysts across multiple industries with specialized tools and methodologies.',
            'feature3-item1': 'Academic Research & Universities',
            'feature3-item2': 'Corporate Market Analysis',
            'feature3-item3': 'Policy & Think Tank Organizations',
            'learn-more3': 'View all industries',
            
            // Resources Section
            'resources': 'Resources',
            'feature4-title': 'Knowledge Center & Support',
            'feature4-desc': 'Access tutorials, research methodologies, case studies, and best practices for qualitative data analysis.',
            'feature4-item1': 'Research Methodology Guides',
            'feature4-item2': 'Training & Tutorials',
            'feature4-item3': 'Case Studies & Best Practices',
            'learn-more4': 'Explore resources',
            
            // Custom Tool Design Section
            'design': 'Design Your Tool',
            'feature5-title': 'Tailored Solutions for Your Research',
            'feature5-desc': 'Request custom-developed tools and modules specifically designed for your research methodology and requirements.',
            'feature5-item1': 'Custom module development',
            'feature5-item2': 'Methodology-specific tools',
            'feature5-item3': 'Workflow integration',
            'learn-more5': 'Start designing',
            
            // Footer
            'lotus-footer': 'Lotus',
            'footer-desc': 'Qualitative Data Analysis Platform<br>Inspired by Ancient Egyptian Knowledge Systems',
            'footer-products': 'Products',
            'footer-product1': 'Lotus Analyzer',
            'footer-product2': 'Lotus Visualizer',
            'footer-product3': 'Lotus Collaborator',
            'footer-pricing': 'Pricing',
            'footer-services': 'Services',
            'footer-service1': 'Research Consulting',
            'footer-service2': 'Implementation',
            'footer-service3': 'Training Programs',
            'footer-service4': 'Methodology Support',
            'footer-company': 'Company',
            'footer-about': 'About Us',
            'footer-contact': 'Contact',
            'footer-team': 'Executive Team',
            'footer-news': 'Newsroom',
            'footer-careers': 'Careers',
            'footer-resources': 'Resources',
            'footer-blog': 'Research Blog',
            'footer-papers': 'Methodology Papers',
            'footer-webinars': 'Webinars',
            'footer-cases': 'Case Studies',
            'copyright': '© 2025 Lotus. All rights reserved.',
            'privacy': 'Privacy Policy',
            'terms': 'Terms of Service',
            'data': 'Data Protection'
        },
        ar: {
            // Navigation
            'lotus': 'لوتس',
            'nav-products': 'المنتجات',
            'nav-services': 'الخدمات',
            'nav-company': 'الشركة',
            'nav-about': 'عن الشركة',
            'nav-contact': 'اتصل بنا',
            'nav-team': 'الفريق التنفيذي',
            'nav-news': 'الأخبار',
            'nav-careers': 'الوظائف',
            'nav-industries': 'القطاعات',
            'nav-resources': 'المصادر',
            'nav-design': 'صمم أداتك',
            'nav-buy': 'شراء',
            'nav-demo': 'طلب تجريبي',
            'search-placeholder': 'ابحث في الأبحاث، التحليلات، الأدوات...',
                
            // Hero section
            'hero-title': 'استكشف لوتس',
            'hero-subtitle': 'منصة مدعومة بالذكاء الاصطناعي للباحثين والأكاديميين لتحليل البيانات النوعية والكمية بدقة',
            'cta-primary': 'ابدأ التحليل',
            'cta-secondary': 'صمم أداتك',
            
            // Products Section
            'products': 'منتجاتنا',
            'feature1-title': 'أدوات تحليل متقدمة مدعومة بالذكاء الاصطناعي',
            'feature1-desc': 'تقدم منصة لوتس تحليلاً شاملاً للبيانات النوعية والكمية باستخدام خوارزميات الذكاء الاصطناعي المتطورة ومعالجة اللغة الطبيعية.',
            'feature1-item1': 'دعم للغتين (العربية والإنجليزية)',
            'feature1-item2': 'معالجة بيانات متعددة التنسيقات',
            'feature1-item3': 'رؤى آلية وتصور بياني',
            'learn-more': 'استكشف جميع المنتجات',
            'learn-more-arrow': '←', // Arrow for products section (RTL)
            
            // Services Section
            'services': 'خدماتنا',
            'feature2-title': 'دعم بحثي شامل',
            'feature2-desc': 'نقدم خدمات شاملة من جمع البيانات إلى التحليل والتصور للفرق البحثية الأكاديمية والمهنية.',
            'feature2-item1': 'تطوير أدوات مخصصة',
            'feature2-item2': 'استشارات بحثية',
            'feature2-item3': 'خدمات التصور البياني',
            'learn-more2': 'اكتشف خدماتنا',
            'learn-more2-arrow': '←', // Arrow for services section (RTL)
            
            // Industries Section
            'industries': 'القطاعات',
            'feature3-title': 'نخدم قطاعات متنوعة',
            'feature3-desc': 'تدعم منصتنا الباحثين والمحللين عبر قطاعات متعددة بأدوات ومنهجيات متخصصة.',
            'feature3-item1': 'البحث الأكاديمي والجامعات',
            'feature3-item2': 'تحليل السوق المؤسسي',
            'feature3-item3': 'منظمات السياسات ومراكز الفكر',
            'learn-more3': 'عرض جميع القطاعات',
            'learn-more3-arrow': '←', // Arrow for industries section (RTL)
            
            // Resources Section
            'resources': 'المصادر',
            'feature4-title': 'مركز المعرفة والدعم',
            'feature4-desc': 'الوصول إلى البرامج التعليمية ومنهجيات البحث ودراسات الحالة وأفضل الممارسات لتحليل البيانات النوعية.',
            'feature4-item1': 'أدلة منهجية البحث',
            'feature4-item2': 'التدريب والبرامج التعليمية',
            'feature4-item3': 'دراسات الحالة وأفضل الممارسات',
            'learn-more4': 'استكشف المصادر',
            'learn-more4-arrow': '←', // Arrow for resources section (RTL)
            
            // Custom Tool Design Section
            'design': 'صمم أداتك',
            'feature5-title': 'حلول مخصصة لبحثك',
            'feature5-desc': 'اطلب أدوات ووحدات مطورة خصيصًا مصممة لمنهجية البحث ومتطلباتك.',
            'feature5-item1': 'تطوير وحدات مخصصة',
            'feature5-item2': 'أدوات خاصة بالمنهجية',
            'feature5-item3': 'تكامل سير العمل',
            'learn-more5': 'ابدأ التصميم',
            'learn-more5-arrow': '←', // Arrow for custom section (RTL)
            
            // Footer
            'lotus-footer': 'لوتس',
            'footer-desc': 'منصة تحليل البيانات النوعية<br>مدعومة بالذكاء الاصطناعي ومعالجة اللغة الطبيعية',
            'footer-products': 'المنتجات',
            'footer-product1': 'محلل لوتس',
            'footer-product2': 'مصور لوتس',
            'footer-product3': 'البيئة التعاونية',
            'footer-pricing': 'التسعير',
            'footer-services': 'الخدمات',
            'footer-service1': 'استشارات البحث',
            'footer-service2': 'التنفيذ',
            'footer-service3': 'برامج التدريب',
            'footer-service4': 'دعم المنهجية',
            'footer-company': 'الشركة',
            'footer-about': 'عننا',
            'footer-contact': 'اتصل',
            'footer-team': 'الفريق التنفيذي',
            'footer-news': 'الأخبار',
            'footer-careers': 'الوظائف',
            'footer-resources': 'المصادر',
            'footer-blog': 'مدونة البحث',
            'footer-papers': 'أوراق منهجية',
            'footer-webinars': 'ندوات عبر الإنترنت',
            'footer-cases': 'دراسات الحالة',
            'copyright': '© 2025 لوتس. جميع الحقوق محفوظة.',
            'privacy': 'سياسة الخصوصية',
            'terms': 'شروط الخدمة',
            'data': 'حماية البيانات'
        }
    };

    // تبديل اللغة
    const languageToggle = document.getElementById('language-toggle');
    let isEnglish = true;
    
    function setLanguage(lang) {
        // تحديث جميع العناصر ذات فئات الترجمة
        Object.keys(translations[lang]).forEach(key => {
            const elements = document.querySelectorAll(`.text-${key}`);
            elements.forEach(element => {
                if (element.tagName === 'INPUT') {
                    element.placeholder = translations[lang][key];
                } else {
                    element.innerHTML = translations[lang][key];
                }
            });
        });
        
        // تحديث اتجاه المستند وسمة اللغة
        document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
        document.documentElement.setAttribute('lang', lang);
        
        // تحديث نص زر التبديل
        languageToggle.textContent = lang === 'en' ? 'العربية' : 'English';
        
        // تحديث الأسهم في روابط "Learn More"
        updateLearnMoreArrows(lang);
        
        // إضافة/إزالة فئة RTL للتنسيق الخاص
        if (lang === 'ar') {
            document.body.classList.add('rtl');
        } else {
            document.body.classList.remove('rtl');
        }
        
        // تخزين تفضيل اللغة
        localStorage.setItem('preferredLanguage', lang);
    }
    
    // دالة لتحديث الأسهم في روابط "Learn More"
    function updateLearnMoreArrows(lang) {
        const learnMoreLinks = [
            { link: '.text-learn-more', arrow: '.text-learn-more-arrow' },
            { link: '.text-learn-more2', arrow: '.text-learn-more2-arrow' },
            { link: '.text-learn-more3', arrow: '.text-learn-more3-arrow' },
            { link: '.text-learn-more4', arrow: '.text-learn-more4-arrow' },
            { link: '.text-learn-more5', arrow: '.text-learn-more5-arrow' }
        ];
        
        learnMoreLinks.forEach(item => {
            const linkElement = document.querySelector(item.link);
            const arrowElement = document.querySelector(item.arrow);
            
            if (linkElement && arrowElement) {
                if (lang === 'en') {
                    linkElement.innerHTML = translations[lang][item.link.replace('.text-', '')] + ' <i class="fas fa-arrow-right"></i>';
                } else {
                    linkElement.innerHTML = '<i class="fas fa-arrow-left"></i> ' + translations[lang][item.link.replace('.text-', '')];
                }
            }
        });
    }
    
    languageToggle.addEventListener('click', function() {
        isEnglish = !isEnglish;
        setLanguage(isEnglish ? 'en' : 'ar');
    });
    
    // تحميل تفضيل اللغة المخزن
    const savedLanguage = localStorage.getItem('preferredLanguage');
    if (savedLanguage) {
        isEnglish = savedLanguage === 'en';
        setLanguage(savedLanguage);
    }
    
    // بقية الكود (نافذة البحث، التمرير السلس، إلخ)...
    // نافذة البحث
    const searchToggle = document.getElementById('search-toggle');
    const searchModal = document.getElementById('search-modal');
    const closeModal = document.querySelector('.close');
    
    if (searchToggle && searchModal && closeModal) {
        searchToggle.addEventListener('click', function() {
            searchModal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
        
        closeModal.addEventListener('click', function() {
            searchModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
        
        window.addEventListener('click', function(event) {
            if (event.target == searchModal) {
                searchModal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    }
    
    // التمرير السلس للتنقل
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                // إغلاق قائمة الجوال إذا كانت مفتوحة
                const hamburger = document.getElementById('hamburger');
                const navMenu = document.getElementById('nav-menu');
                
                if (hamburger && navMenu) {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                    navMenu.style.left = '-100%';
                }
                
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // تبديل قائمة الجوال
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
            
            if (navMenu.classList.contains('active')) {
                navMenu.style.left = '0';
            } else {
                navMenu.style.left = '-100%';
            }
        });
    }
    
    // القائمة المنسدلة للجوال
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            if (window.innerWidth <= 992) {
                e.preventDefault();
                e.stopPropagation();
                this.classList.toggle('active');
            }
        });
    });
    
    // إغلاق القائمة المنسدلة عند النقر خارجها
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 992) {
            dropdowns.forEach(dropdown => {
                if (!dropdown.contains(e.target)) {
                    dropdown.classList.remove('active');
                }
            });
        }
    });
    
    // تحميل الصور عند الحاجة
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.src;
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // إضافة حركة خفيفة للأقسام عند التمرير
    const animateOnScroll = function() {
        const sections = document.querySelectorAll('.content-section');
        
        sections.forEach(section => {
            const sectionTop = section.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (sectionTop < windowHeight * 0.85) {
                section.style.opacity = 1;
                section.style.transform = 'translateY(0)';
            }
        });
    };
    
    // تهيئة الأقسام للحركة
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.opacity = 0;
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
    
    window.addEventListener('scroll', animateOnScroll);
    // تشغيل مرة واحدة عند التحميل
    setTimeout(animateOnScroll, 100);
});