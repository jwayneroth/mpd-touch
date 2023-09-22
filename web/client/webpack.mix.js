let mix = require('laravel-mix');

mix.js('src/js/app.js', 'public/js/app.js')
	.sass('src/scss/app.scss', 'public/css/app.css')
	.copyDirectory('src/images', 'public/images')
	.copyDirectory('src/fonts', 'public/fonts')
	.options({
		processCssUrls: false,
		manifest: false
	});