// Logo de la veterinaria: una huellita (dibujada en SVG, sin imágenes externas)
export default function Logo({ tamano = 36 }) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 64 64" role="img" aria-label="Logo de la veterinaria">
      <defs>
        <linearGradient id="degradeLogo" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#DF6D41" />
          <stop offset="100%" stopColor="#E9A75A" />
        </linearGradient>
      </defs>
      <circle cx="32" cy="32" r="31" fill="#ffffff" />
      <g fill="url(#degradeLogo)">
        {/* Almohadilla principal */}
        <path d="M32 33c-7.5 0-14 7.2-14 12.6 0 4.6 4.2 6.4 7.6 5.4 2.4-.7 4.2-1.9 6.4-1.9s4 1.2 6.4 1.9c3.4 1 7.6-.8 7.6-5.4C46 40.2 39.5 33 32 33z" />
        {/* Deditos */}
        <ellipse cx="18.5" cy="27" rx="4.6" ry="6" transform="rotate(-25 18.5 27)" />
        <ellipse cx="26.5" cy="18.5" rx="4.8" ry="6.4" transform="rotate(-8 26.5 18.5)" />
        <ellipse cx="37.5" cy="18.5" rx="4.8" ry="6.4" transform="rotate(8 37.5 18.5)" />
        <ellipse cx="45.5" cy="27" rx="4.6" ry="6" transform="rotate(25 45.5 27)" />
      </g>
    </svg>
  )
}
