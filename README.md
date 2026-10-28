# Mellow KR | Shopee image assets

This repository is used to publish verified product image assets for Shopee listings via Render Static Site.

- `public/images/<product-id>/<01-06>.jpg`: final approved product thumbnails (pending upload)
- `public/asset-manifest.json`: expected image paths and SHA-256 hashes
- `public/index.html`: service index

Only publish verified product photographs and edited thumbnails. A working image URL must respond anonymously with an actual image file. Do not treat a successful deploy without 30 image assets as complete.
