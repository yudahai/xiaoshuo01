$(document).ready(
  ->
    have_read = localStorage['have_read'].split(' ')
    console.log(have_read)
    $('a.bg-info').each(
      ->
        chapter_id = $(this).attr('chapter_id')
        if chapter_id in have_read
          $(this).attr('class', 'bg-success')
          $(this).attr('<span class="btn-success">已读</span>')
        return
    )
)