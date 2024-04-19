# Maintainer: KorryKatti 8nctvx7gi@mozmail.com
pkgname=thunder
pkgver=0.0
pkgrel=1
pkgdesc="An App Store For Python Projects"
arch=('any')
url="https://github.com/KorryKatti/Thunder"
license=('MIT')
depends=('tk')
source=("$url/releases/download/Debut/Thunder0.0.0.tar")
sha256sums=('SKIP')

prepare() {
    cd "$srcdir"
    git clone "$url" "Thunder-$pkgver"
}

package() {
    cd "$srcdir/Thunder-$pkgver"
    chmod +x run.sh
    mkdir -p "$pkgdir$HOME/.local/share/thunder"  # Install under the user's home directory
    cp -r * "$pkgdir$HOME/.local/share/thunder/"
}
