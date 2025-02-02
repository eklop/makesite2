#!/usr/bin/env python

import os,shutil,re,glob,sys,json,datetime

def fread(filename):
    """Read file and close the file."""
    with open(filename, 'r') as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    with open(filename, 'w') as f:
        f.write(text)


def log(msg, *args):
    """Log message with specified arguments."""
    sys.stderr.write(msg.format(*args) + '\n')


def truncate(text, words=25):
    """Remove tags and truncate text to the specified number of words."""
    return ' '.join(re.sub('(?s)<.*?>', ' ', text).split()[:words])


def read_headers(text):
    """Parse headers in text and yield (key, value, end-index) tuples."""
    for match in re.finditer(r'\s*<!--\s*(.+?)\s*:\s*(.+?)\s*-->\s*|.+', text):
        if not match.group(1):
            break
        yield match.group(1), match.group(2), match.end()


def format_date(date_str, date_format='%a, %d %b %Y %H:%M:%S +0000'):
    """Convert yyyy-mm-dd date string to RFC 2822 format date string."""
    d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return d.strftime(date_format)


def read_content(filename):
    global params
    """Read content and metadata from file into a dictionary."""
    # Read file content.
    text = fread(filename)

    # Read metadata and save it in a dictionary.
    date_slug = os.path.basename(filename).split('.')[0]
    match = re.search(r'^(?:(\d\d\d\d-\d\d-\d\d)-)?(.+)$', date_slug)
    content = {
        'date': match.group(1) or '1970-01-01',
        'slug': match.group(2),
    }

    # Read headers.
    end = 0
    for key, val, end in read_headers(text):
        content[key] = val

    # Separate content from headers.
    text = text[end:]

    # Convert Markdown content to HTML.
    if filename.endswith(('.md', '.mkd', '.mkdn', '.mdown', '.markdown')):
        try:
            import commonmark
            text = commonmark.commonmark(text)
        except ImportError as e:
            log('WARNING: Cannot render Markdown in {}: {}', filename, str(e))

    # Update the dictionary with content and RFC 2822 date.
    content.update({
        'content': text,
        'pretty_date':format_date(content['date'], params['pretty_date_format']),
        'rfc_2822_date': format_date(content['date'])
    })

    return content


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(r'{{\s*([^}\s]+)\s*}}',
                  lambda match: str(params.get(match.group(1), match.group(0))),
                  template)


def make_pages(src, dst, layout, **params):
    """Generate pages from page content."""
    items = []

    for src_path in glob.glob(src):
        content = read_content(src_path)

        page_params = dict(params, **content)

        # Populate placeholders in content if content-rendering is enabled.
        if page_params.get('render') == 'yes':
            rendered_content = render(page_params['content'], **page_params)
            page_params['content'] = rendered_content
            content['content'] = rendered_content

        items.append(content)

        dst_path = render(dst, **page_params)
        output = render(layout, **page_params)

        log('Rendering {} => {} ...', src_path, dst_path)
        fwrite(dst_path, output)

    return sorted(items, key=lambda x: x['date'], reverse=True)


def make_list(posts, dst, list_layout, item_layout, **params):
    """Generate list page for a blog."""
    items = []
    for post in posts:
        item_params = dict(params, **post)
        item_params['summary'] = truncate(post['content'])
        item = render(item_layout, **item_params)
        items.append(item)

    params['content'] = ''.join(items)
    dst_path = render(dst, **params)
    output = render(list_layout, **params)

    log('Rendering list => {} ...', dst_path)
    fwrite(dst_path, output)


def main():
    global params
    # Default parameters.
    params = {
        'site_title':'Lorem Ipsum',
        'subtitle': 'Dolor sit amet',
        'output_dir':'_site',
        'theme':'default',
        'author': 'Admin',
        'pretty_date_format':'%d %b %Y',
        'site_url': 'http://localhost:8000',
        'current_year': datetime.datetime.now().year
    }

    if not all(params.values()):
        print("Some values are empty in the param object..")
        sys.exit(0)
    
    params['base_path'] = ''

    # If params.json exists, load it.
    if os.path.isfile('params.json'):
        params.update(json.loads(fread('params.json')))

    if not os.path.exists('themes/'+params['theme']):
        raise FileNotFoundError("Theme folder '{0}' not found in /themes".format(params['theme']))
    else:
        theme_path = 'themes/'+params['theme']+'/'

    # Create a new output directory from scratch.
    if os.path.isdir(params['output_dir']):
        shutil.rmtree(params['output_dir'])

    shutil.copytree('static', params['output_dir'])
    
    if os.path.exists(theme_path+'static'):
        shutil.copytree(theme_path+'static', params['output_dir']+'/'+params['theme'])

    # Load layouts.
    try:
        page_layout = fread(theme_path+'page.html')
        post_layout = fread(theme_path+'post.html')
        list_layout = fread(theme_path+'list.html')
        item_layout = fread(theme_path+'item.html')
        feed_xml = fread(theme_path+'feed.xml')
        item_xml = fread(theme_path+'item.xml')
    except FileNotFoundError as e:
        raise FileNotFoundError(e)

    # Combine layouts to form final layouts.
    post_layout = render(page_layout, content=post_layout)
    list_layout = render(page_layout, content=list_layout)

    # Create site pages.
    make_pages('content/_index.html', str(params['output_dir']+'/index.html'),
               page_layout, **params)
    make_pages('content/[!_]*.html', str(params['output_dir']+'/{{ slug }}/index.html'),
               page_layout, **params)

    # Create blogs.
    blog_posts = make_pages('content/blog/*.md',
                            str(params['output_dir']+'/blog/{{ slug }}/index.html'),
                            post_layout, blog='blog', **params)

    # Create blog list pages.
    make_list(blog_posts, str(params['output_dir']+'/blog/index.html'),
              list_layout, item_layout, blog='blog', title='Blog', **params)

    # Create RSS feeds.
    make_list(blog_posts, str(params['output_dir']+'/blog/rss.xml'),
              feed_xml, item_xml, blog='blog', title='Blog', **params)

if __name__ == '__main__':
    main()
