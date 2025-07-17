# Bourracho Frontend

React + TypeScript + Vite frontend for the Bourracho application.

## Prerequisites

- **Node.js** (v22.12.0 or higher) - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js)

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be served at `http://localhost:5173`

## Available Scripts

### Dev

```bash
# Start development server
npm run dev

# Start development server with host access (for mobile testing)
npm run dev:host

# Preview production build locally
npm run preview
```

### Building

```bash
# Build for production
npm run build
```

### Code Quality

```bash
# Lint code
npm run lint

# Fix linting issues automatically
npm run lint:fix

# Format code with Prettier
npm run format

# Check code formatting
npm run format:check
```

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **ESLint** - Linting
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI component library
- **Radix UI** - Headless UI primitives
- **Lucide React** - Icons

## Development

### Backend Integration

The frontend connects to the Django backend running on `http://localhost:8000`. Make sure the backend is running before testing frontend features.

### Environment Variables

Create a `.env` file in the frontend directory if you need to configure environment-specific variables:

```env
VITE_API_URL=http://localhost:8000
```

### Adding New Components

This project uses shadcn/ui for consistent component design. To add new components:

```bash
npx shadcn@latest add [component-name]
```

See [documentation](https://ui.shadcn.com/docs/installation/vite#add-components)

### Styling

- Use Tailwind CSS classes for styling
- Follow the existing component patterns in `src/components/ui/`
- Use the theme provider for dark/light mode support

## Building for Production

```bash
# Build the application
npm run build

# Preview the production build
npm run preview
```

The built files will be in the `dist/` directory.

## Troubleshooting

### Common Issues

1. **Port already in use**: If port 5173 is already in use:

   ```bash
   npm run dev -- --port 3000
   ```

2. **Dependencies issues**: If you encounter dependency problems:

   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **TypeScript errors**: Run the linter to identify issues:

   ```bash
   npm run lint
   ```

4. **Build errors**: Check that all imports are correct and TypeScript types are properly defined.

## Contributing

1. Follow the existing code style and patterns
2. Run linting before committing: `npm run lint`
3. Format your code: `npm run format`
4. Test your changes thoroughly
