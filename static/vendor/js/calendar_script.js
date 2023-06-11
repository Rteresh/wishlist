document.addEventListener("DOMContentLoaded", function () {
  var currentDate = new Date(); // Получаем текущую дату

  // Установка текущего года в заголовок
  var yearElement = document.querySelector(".year");
  yearElement.textContent = currentDate.getFullYear();

  // Установка текущего месяца и дня в заголовок
  var monthElement = document.querySelector(".months li a[data-value='" + (currentDate.getMonth() + 1) + "']");
  monthElement.classList.add("active"); // Добавляем класс "active" текущему месяцу

  // Генерация календарных дней
  generateCalendarDays(currentDate.getMonth() + 1, currentDate.getDate());
});

function generateCalendarDays(month, currentDay) {
  var daysElement = document.querySelector(".days");
  daysElement.innerHTML = ""; // Очищаем контейнер для дней

  var totalDays = new Date(new Date().getFullYear(), month, 0).getDate(); // Получаем общее количество дней в выбранном месяце

  for (var i = 1; i <= totalDays; i++) {
    var dayElement = document.createElement("li");
    dayElement.textContent = i;

    if (i === currentDay) {
      dayElement.classList.add("active"); // Добавляем класс "active" текущему дню
    }

    daysElement.appendChild(dayElement);
  }
}

// Обработчик клика на месяц
var monthLinks = document.querySelectorAll(".months li a");
monthLinks.forEach(function (monthLink) {
  monthLink.addEventListener("click", function (event) {
    event.preventDefault();

    var month = parseInt(event.target.getAttribute("data-value"), 10);
    var currentDay = 1; // Устанавливаем текущий день в 1

    // Удаление класса "active" у всех месяцев
    monthLinks.forEach(function (link) {
      link.classList.remove("active");
    });

    event.target.classList.add("active"); // Добавляем класс "active" выбранному месяцу

    generateCalendarDays(month, currentDay);
  });
});
