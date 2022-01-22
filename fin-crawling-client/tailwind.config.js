module.exports = {
  // content: process.env.mode=="production"?['./src/**/*.html','./src/**/*.tsx'
  // ,'./src/**/*.jsx','./src/**/*.js','./src/**/*.css']:null,

  content: ['./src/**/*.html','./src/**/*.tsx'
  ,'./src/**/*.jsx','./src/**/*.js','./src/**/*.css'],
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
