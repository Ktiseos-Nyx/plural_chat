This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## 🎨 Lobe UI Integration

This project uses [Lobe UI](https://github.com/lobehub/lobe-ui) for the chat interface. **Important setup requirements:**

### Required Dependencies

Make sure your `package.json` includes:

```json
{
  "dependencies": {
    "@lobehub/ui": "^2.13.6",
    "@lobehub/icons": "^2.43.1",
    "antd": "^5.22.6",           // REQUIRED: Lobe UI peer dependency
    "antd-style": "^3.7.1",
    // ... other deps
  }
}
```

**Note:** Ant Design (`antd`) is a **required peer dependency** for Lobe UI. The app will not work without it.

### Next.js Configuration

Your `next.config.ts` **must** include transpilePackages for Lobe UI (ESM-only package):

```typescript
const nextConfig: NextConfig = {
  transpilePackages: ['@lobehub/ui', '@lobehub/icons', 'antd-style'],
  // ... other config
};
```

Without this, you'll get ESM import errors in production builds.

## Getting Started

First, install dependencies:

```bash
npm install
# or
bun install
```

Then run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
