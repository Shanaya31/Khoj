/** Palette taken from Mumbai itself: monsoon sky, sea-wall concrete, kaali-peeli taxi yellow. */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#14232A",
        sea: "#1E6B73",
        wall: "#E4E6E1",
        taxi: "#F4B400",
        monsoon: "#51656B",
      },
      fontFamily: {
        display: ['"Bricolage Grotesque"', "system-ui", "sans-serif"],
        story: ["Newsreader", "Georgia", "serif"],
        deva: ['"Tiro Devanagari Hindi"', '"Noto Serif Devanagari"', "serif"],
      },
    },
  },
  plugins: [],
};
