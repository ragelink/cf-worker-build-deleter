        while True:
            params = {
                "page": page,
                "per_page": min(self.limit, 25)  # Cloudflare API limit is 25 per page for this endpoint
            }
            
            if self.env:
                params["env"] = self.env 