{
  "name": "thirdvoice-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "build:cf": "CF_PAGES=1 next build && CF_PAGES=1 next-on-pages",
    "build:vercel": "next build",
    "start": "next start",
    "test": "jest --watchAll=false --passWithNoTests",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "autoprefixer": "^10.4.21",
    "lucide-react": "^0.541.0",
    "next": "15.5.0",
    "next-pwa": "^5.6.0",
    "postcss": "^8.5.6",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwindcss": "^3.4.17"
  },
  "devDependencies": {
    "@babel/core": "^7.23.0",
    "@babel/preset-env": "^7.23.0",
    "@babel/preset-react": "^7.22.0",
    "@babel/preset-typescript": "^7.23.0",
    "@eslint/eslintrc": "^3",
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^14.5.2",
    "@types/jest": "^29.5.12",
    "@types/next-pwa": "^5.6.9",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18.2.7",
    "babel-jest": "^29.7.0",
    "eslint": "^9",
    "eslint-config-next": "15.5.0",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "typescript": "^5"
  },
  "optionalDependencies": {
    "@cloudflare/next-on-pages": "^1.8.0",
    "wrangler": "^3.0.0"
  }
}