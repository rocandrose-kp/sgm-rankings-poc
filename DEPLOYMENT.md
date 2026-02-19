# Deploying Tournament Rankings to GitHub Pages

This guide will help you deploy the Tournament Rankings application to GitHub Pages.

## Prerequisites

1. A GitHub account
2. Git installed on your computer
3. The project files (already in `c:\xampp\htdocs\sgm-poc\tournament-rankings-poc\web`)

## Deployment Steps

### Option 1: Automatic Deployment with GitHub Actions (Recommended)

This method automatically deploys your app whenever you push to the main branch.

1. **Create a GitHub Repository**
   - Go to https://github.com/new
   - Name it `sgm-poc` (or any name you prefer)
   - Make it public or private
   - Don't initialize with README (we already have files)

2. **Initialize Git and Push to GitHub**
   ```bash
   cd c:\xampp\htdocs\sgm-poc
   git init
   git add .
   git commit -m "Initial commit - Tournament Rankings App"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/sgm-poc.git
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Under "Source", select **GitHub Actions**

4. **Update Configuration**
   - Edit `tournament-rankings-poc/web/vite.config.ts`
   - Change `base: '/sgm-poc/'` to match your repository name
   - Edit `tournament-rankings-poc/web/package.json`
   - Update `homepage` to: `https://YOUR_USERNAME.github.io/REPO_NAME`

5. **Push Changes**
   ```bash
   git add .
   git commit -m "Configure for GitHub Pages deployment"
   git push
   ```

6. **Wait for Deployment**
   - Go to **Actions** tab in your repository
   - Watch the deployment workflow run
   - Once complete, your app will be live at: `https://YOUR_USERNAME.github.io/sgm-poc`

### Option 2: Manual Deployment with gh-pages

1. **Install gh-pages package**
   ```bash
   cd c:\xampp\htdocs\sgm-poc\tournament-rankings-poc\web
   npm install --save-dev gh-pages
   ```

2. **Build and Deploy**
   ```bash
   npm run deploy
   ```

3. **Enable GitHub Pages**
   - Go to repository **Settings** → **Pages**
   - Under "Source", select **Deploy from a branch**
   - Select branch: `gh-pages` and folder: `/ (root)`
   - Click **Save**

## Configuration Files Created

- `.github/workflows/deploy.yml` - GitHub Actions workflow for automatic deployment
- `vite.config.ts` - Updated with base path for GitHub Pages
- `package.json` - Added deploy script and homepage field

## Important Notes

1. **Base Path**: The app is configured to run at `/sgm-poc/`. If you use a different repository name, update:
   - `vite.config.ts`: Change `base: '/sgm-poc/'`
   - `package.json`: Update the `homepage` URL

2. **Router Configuration**: The app uses React Router with BrowserRouter. GitHub Pages works best with HashRouter for client-side routing, but the current setup should work with the GitHub Actions deployment.

3. **Custom Domain** (Optional): You can add a custom domain in GitHub Pages settings if you own one.

## Troubleshooting

**404 on page refresh**: If you get 404 errors when refreshing pages, you may need to:
- Switch to HashRouter in `App.tsx`, or
- Add a custom 404.html that redirects to index.html

**Build fails**: Check that all dependencies are installed:
```bash
cd tournament-rankings-poc/web
npm install
npm run build
```

**Wrong base path**: If assets don't load, verify the `base` in `vite.config.ts` matches your repository name.

## Updating the Deployed App

After making changes:
```bash
git add .
git commit -m "Your commit message"
git push
```

The GitHub Actions workflow will automatically rebuild and redeploy your app.

## Local Testing Before Deployment

Test the production build locally:
```bash
npm run build
npm run preview
```

This will serve the built app at http://localhost:4173 (or similar) so you can verify it works correctly before deploying.
