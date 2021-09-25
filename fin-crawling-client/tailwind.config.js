module.exports = {
  purge: {
    enabled: process.env.mode=="production",
    content: ['./src/**/*.html','./src/**/*.tsx'
    ,'./src/**/*.jsx','./src/**/*.js','./src/**/*.css'],
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {
      backgroundColor: ['checked'],
      borderColor: ['checked'],
    },
  },
  plugins: [],
}
