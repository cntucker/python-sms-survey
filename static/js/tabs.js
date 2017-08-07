$(document).ready(function() {
    // Calculate tab widths
    $('.tabbed.horizontal').each(function(){
        var numTabs = $(this).find('.tab').length;
        var percentWidth = (100/numTabs).toString() + "%";
        $(this).find('.tab').each(function(){
            $(this).css('width', percentWidth);
        });
        $(this).find('.tabs').css('margin-right', '-' + (numTabs - 1) + 'px');
    });

    // Click tab
    $('.tabbed .tab:not(.disabled)').click(function(){
        if (!$(this).hasClass('active')) {
            var tabNum = this.className.match(/t(\d+)/)[1];
            // Change active tab
            $(this).siblings('.tab').removeClass('active');
            $(this).addClass('active');
            // Change active content
            $(this).parents('.tabbed').find('.content').removeClass('active');
            $(this).parents('.tabbed').find('.c' + tabNum).addClass('active');
        }
    });
});
