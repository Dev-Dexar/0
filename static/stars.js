function createStars(count) {
    const starsContainer = document.getElementById("stars");
    for (let i = 0; i < count; i++) {
        let star = document.createElement("div");
        star.className = "star";
        star.style.top = Math.random() * 100 + "%";
        star.style.left = Math.random() * 100 + "%";
        star.style.animationDuration = (Math.random() * 3 + 2) + "s";
        starsContainer.appendChild(star);
    }
}
createStars(150);